// PRD Copilot 本地控制台 —— 薄壳：浏览器聊天 UI ⇄ Claude Agent SDK ⇄ prd-copilot skill
// 设计约束：不复制任何提示词。skill（~/.claude/skills/prd-copilot）是唯一真相源，本服务只负责对话搬运。
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFile } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { query } from '@anthropic-ai/claude-agent-sdk';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 4870);
const WORKDIR = path.resolve(process.env.PRD_WORKDIR || process.cwd());
const PRDS_DIR = path.join(WORKDIR, 'prds');
const SKILL_PATH = path.join(os.homedir(), '.claude', 'skills', 'prd-copilot', 'SKILL.md');
const STRIP_ENV = process.env.PRD_STRIP_ANTHROPIC_ENV === '1';

// 传给 SDK 子进程的环境：默认原样继承（尊重用户 shell）；PRD_STRIP_ANTHROPIC_ENV=1 时剥掉第三方端点残留，强制走官方登录
function childEnv() {
  const env = { ...process.env };
  if (STRIP_ENV) for (const k of Object.keys(env)) if (/^ANTHROPIC_(BASE_URL|AUTH_TOKEN|API_KEY|MODEL|DEFAULT_.*_MODEL|REASONING_MODEL)$/.test(k)) delete env[k];
  return env;
}
function detectedOverrides() {
  return Object.keys(process.env).filter(k => /^ANTHROPIC_(BASE_URL|AUTH_TOKEN|API_KEY|MODEL|DEFAULT_.*_MODEL)$/.test(k));
}

// ---------- 会话：每个浏览器会话 = 一个 SDK query（流式输入保持长连） ----------
const sessions = new Map(); // key -> { clients:Set<res>, queue:[], waiter, q, pending:Map<requestId,resolve>, abort, started }
function session(key) {
  if (!sessions.has(key)) sessions.set(key, { clients: new Set(), queue: [], waiter: null, q: null, pending: new Map(), abort: null, started: false, closed: false });
  return sessions.get(key);
}
function emit(s, ev) { const line = `data: ${JSON.stringify(ev)}\n\n`; for (const res of s.clients) res.write(line); }

async function* inputStream(s) {
  while (!s.closed) {
    if (s.queue.length) { yield s.queue.shift(); continue; }
    await new Promise(r => { s.waiter = r; });
    s.waiter = null;
  }
}
function pushUser(s, text) {
  s.queue.push({ type: 'user', message: { role: 'user', content: text }, parent_tool_use_id: null });
  if (s.waiter) s.waiter();
}

const ALLOWED = ['Read', 'Write', 'Edit', 'MultiEdit', 'Grep', 'Glob', 'Bash', 'Agent', 'Task', 'Skill', 'TodoWrite', 'WebFetch', 'WebSearch', 'NotebookEdit'];
const TOOL_LABEL = { Read: '读取', Write: '写入', Edit: '编辑', MultiEdit: '编辑', Grep: '扫描', Glob: '检索', Bash: '命令', Agent: '独立评审子代理', Task: '独立评审子代理', Skill: '加载 skill', TodoWrite: '计划', WebFetch: '抓取', WebSearch: '搜索' };
function toolSummary(name, input) {
  const i = input || {};
  const short = p => typeof p === 'string' ? path.basename(p) : '';
  if (name === 'Skill') return `⚡ 加载 skill：${i.skill || ''}`;
  if (name === 'Write') return `✍️ 写入 ${short(i.file_path)}`;
  if (name === 'Edit' || name === 'MultiEdit') return `✏️ 编辑 ${short(i.file_path)}`;
  if (name === 'Read') return `📖 读取 ${short(i.file_path)}`;
  if (name === 'Grep') return `🔍 扫描「${String(i.pattern || '').slice(0, 24)}」`;
  if (name === 'Bash') return `⌘ ${String(i.description || i.command || '').slice(0, 40)}`;
  if (name === 'Agent' || name === 'Task') return `🧪 子代理：${String(i.description || '').slice(0, 30)}`;
  return `${TOOL_LABEL[name] || name}`;
}

function startQuery(s, key) {
  s.started = true; s.abort = new AbortController();
  const opts = {
    cwd: WORKDIR,
    settingSources: ['user', 'project'],
    skills: ['prd-copilot'],
    allowedTools: ALLOWED,
    permissionMode: 'default',
    includePartialMessages: true,
    persistSession: true,
    abortController: s.abort,
    env: childEnv(),
    ...(process.env.PRD_MODEL ? { model: process.env.PRD_MODEL } : {}),
    ...(claudeBin() ? { pathToClaudeCodeExecutable: claudeBin() } : {}),
    systemPrompt: {
      type: 'preset', preset: 'claude_code',
      append: [
        '你正运行在「PRD Copilot 控制台」——一个本地网页聊天壳。用户看不到终端，只看到你的文本、工具活动摘要和 AskUserQuestion 弹出的问题卡片。',
        '凡是用户要 PRD / 需求文档 / 把想法整理成文档，一律调用 prd-copilot skill 并严格按其管线执行（含三道质量门与独立评审子代理）。',
        `产出目录固定为 ${PRDS_DIR}（不存在则创建）。inbox 在 ${WORKDIR} 或其上一级查找。`,
        '澄清问题必须用 AskUserQuestion 工具提出（用户在网页上答题），不要在正文里列问题等用户回复。',
        '正文用简体中文，简洁；过程性播报每道门一行即可。'
      ].join('\n')
    },
    canUseTool: async (toolName, input, { signal }) => {
      if (toolName === 'AskUserQuestion') {
        const requestId = `q${Date.now()}${Math.random().toString(36).slice(2, 7)}`;
        (s._lastQuestions ||= {})[requestId] = input.questions || [];
        emit(s, { type: 'question', requestId, questions: input.questions || [] });
        return new Promise((resolve) => {
          s.pending.set(requestId, resolve);
          signal.addEventListener('abort', () => { s.pending.delete(requestId); resolve({ behavior: 'deny', message: '用户取消' }); }, { once: true });
        });
      }
      if (ALLOWED.includes(toolName)) return { behavior: 'allow', updatedInput: input };
      return { behavior: 'deny', message: `控制台未授权工具 ${toolName}；请用已授权工具完成，或向用户说明。` };
    },
  };

  (async () => {
    try {
      s.q = query({ prompt: inputStream(s), options: opts });
      for await (const m of s.q) {
        if (m.type === 'system' && m.subtype === 'init') {
          emit(s, { type: 'system', text: `运行时 ${m.claude_code_version} · 模型 ${m.model} · 凭据 ${m.apiKeySource}` });
          const skills = m.skills || m.slash_commands || [];
          if (!skills.some(x => String(x).includes('prd-copilot'))) emit(s, { type: 'system', text: '⚠ 本会话未加载到 prd-copilot skill（检查 ~/.claude/skills 链接）' });
          continue;
        }
        if (m.type === 'stream_event') {
          const e = m.event; if (m.parent_tool_use_id) continue; // 子代理内部不透传
          if (e.type === 'content_block_delta' && e.delta?.type === 'text_delta') emit(s, { type: 'text_delta', text: e.delta.text });
          continue;
        }
        if (m.type === 'assistant' && !m.parent_tool_use_id) {
          for (const b of m.message?.content || []) if (b.type === 'tool_use') emit(s, { type: 'tool', name: b.name, summary: toolSummary(b.name, b.input) });
          continue;
        }
        if (m.type === 'result') {
          if (m.is_error || m.subtype !== 'success') {
            const detail = [m.subtype !== 'success' ? m.subtype : null, ...(m.errors || []), m.result].filter(Boolean).join('\n');
            emit(s, { type: 'error', message: `本轮未完成：${detail || '未知错误'}` });
          }
          else emit(s, { type: 'result', num_turns: m.num_turns, duration_s: m.duration_ms ? Math.round(m.duration_ms / 1000) : null, cost: m.total_cost_usd ? m.total_cost_usd.toFixed(3) : null, session_id: m.session_id });
          continue;
        }
      }
      emit(s, { type: 'session_end' });
    } catch (err) {
      emit(s, { type: 'error', message: `运行时错误：${err?.message || err}` });
    } finally { s.started = false; s.q = null; }
  })();
}

// ---------- 状态与文件 ----------
function claudeBin() {
  if (process.env.PRD_CLAUDE_BIN) return process.env.PRD_CLAUDE_BIN;
  const bundled = path.join(__dirname, 'node_modules', '@anthropic-ai', `claude-agent-sdk-${process.platform}-${process.arch}`, 'claude');
  if (fs.existsSync(bundled)) return bundled;
  // 捆绑二进制缺失（如 npm 可选依赖下载失败）→ 回落到 PATH 里的系统 claude
  for (const dir of (process.env.PATH || '').split(path.delimiter)) {
    const cand = path.join(dir, 'claude'); try { if (fs.statSync(cand).isFile()) return fs.realpathSync(cand); } catch {}
  }
  return null;
}
function authStatus() {
  return new Promise(resolve => {
    const bin = claudeBin(); if (!bin) return resolve({ loggedIn: false, authMethod: 'none', error: 'claude 可执行文件未找到' });
    execFile(bin, ['auth', 'status'], { env: childEnv(), timeout: 15000 }, (err, stdout) => {
      try { const j = JSON.parse(stdout); resolve({ loggedIn: !!j.loggedIn, authMethod: j.authMethod, apiProvider: j.apiProvider }); }
      catch { resolve({ loggedIn: false, authMethod: 'unknown', error: err?.message || String(stdout).slice(0, 120) }); }
    });
  });
}
function listPrds() {
  if (!fs.existsSync(PRDS_DIR)) return [];
  return fs.readdirSync(PRDS_DIR).filter(f => f.endsWith('.md')).map(f => { const st = fs.statSync(path.join(PRDS_DIR, f)); return { name: f, size: st.size, mtimeMs: st.mtimeMs, mtime: st.mtime.toISOString().slice(0, 16).replace('T', ' ') }; }).sort((a, b) => b.mtimeMs - a.mtimeMs);
}
function safePrd(name) { const base = path.basename(name); if (!base.endsWith('.md') || base !== name) return null; const p = path.join(PRDS_DIR, base); return fs.existsSync(p) ? p : null; }
function json(res, code, obj) { res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(obj)); }
function body(req) { return new Promise((resolve, reject) => { let d = ''; req.on('data', c => { d += c; if (d.length > 2e6) req.destroy(); }); req.on('end', () => { try { resolve(d ? JSON.parse(d) : {}); } catch (e) { reject(e); } }); }); }

// ---------- HTTP ----------
const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, `http://127.0.0.1:${PORT}`);
  try {
    if (req.method === 'GET' && u.pathname === '/') { res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' }); return res.end(fs.readFileSync(path.join(__dirname, 'public', 'index.html'))); }
    if (req.method === 'GET' && u.pathname === '/api/status') {
      const a = await authStatus();
      return json(res, 200, { ...a, workdir: WORKDIR, workdirShort: WORKDIR.replace(os.homedir(), '~'), prdsDir: PRDS_DIR, skillFound: fs.existsSync(SKILL_PATH), claudeBin: claudeBin(), anthropicEnvOverrides: detectedOverrides(), stripEnv: STRIP_ENV, model: process.env.PRD_MODEL || null });
    }
    if (req.method === 'GET' && u.pathname === '/api/events') {
      const s = session(u.searchParams.get('s') || 'default');
      res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
      res.write(': connected\n\n'); s.clients.add(res);
      const ping = setInterval(() => res.write(': ping\n\n'), 20000);
      req.on('close', () => { clearInterval(ping); s.clients.delete(res); });
      return;
    }
    if (req.method === 'POST' && u.pathname === '/api/chat') {
      const { s: key = 'default', text } = await body(req);
      if (!text || typeof text !== 'string') return json(res, 400, { error: 'text required' });
      const s = session(key); s.closed = false;
      pushUser(s, text); if (!s.started) startQuery(s, key);
      return json(res, 200, { ok: true });
    }
    if (req.method === 'POST' && u.pathname === '/api/answer') {
      const { s: key = 'default', requestId, answers = {}, response } = await body(req);
      const s = session(key); const resolve = s.pending.get(requestId);
      if (!resolve) return json(res, 404, { error: 'no pending question' });
      s.pending.delete(requestId);
      // 按 SDK 契约：必须回传原 questions；answers 以问题原文为键；response 为整体自由回复
      const q = s._lastQuestions?.[requestId] || [];
      resolve({ behavior: 'allow', updatedInput: response ? { questions: q, answers, response } : { questions: q, answers } });
      return json(res, 200, { ok: true });
    }
    if (req.method === 'POST' && u.pathname === '/api/interrupt') {
      const { s: key = 'default' } = await body(req); const s = session(key);
      try { await s.q?.interrupt?.(); } catch {}
      return json(res, 200, { ok: true });
    }
    if (req.method === 'POST' && u.pathname === '/api/reset') {
      const { s: key = 'default' } = await body(req); const s = sessions.get(key);
      if (s) { s.closed = true; if (s.waiter) s.waiter(); try { s.abort?.abort(); } catch {} sessions.delete(key); }
      return json(res, 200, { ok: true });
    }
    if (req.method === 'GET' && u.pathname === '/api/files') return json(res, 200, listPrds());
    if (req.method === 'GET' && u.pathname === '/api/file') {
      const p = safePrd(u.searchParams.get('name') || ''); if (!p) return json(res, 404, { error: 'not found' });
      res.writeHead(200, { 'Content-Type': 'text/markdown; charset=utf-8', ...(u.searchParams.get('download') ? { 'Content-Disposition': `attachment; filename*=UTF-8''${encodeURIComponent(path.basename(p))}` } : {}) });
      return res.end(fs.readFileSync(p));
    }
    res.writeHead(404); res.end('not found');
  } catch (err) { json(res, 500, { error: err?.message || String(err) }); }
});

server.listen(PORT, '127.0.0.1', async () => {
  fs.mkdirSync(PRDS_DIR, { recursive: true });
  const a = await authStatus();
  console.log(`PRD Copilot 控制台  →  http://127.0.0.1:${PORT}`);
  console.log(`工作目录 ${WORKDIR}  ·  产出 ${PRDS_DIR}`);
  console.log(`skill ${fs.existsSync(SKILL_PATH) ? '✓ ' + SKILL_PATH : '✗ 未找到 ' + SKILL_PATH}`);
  console.log(`claude ${claudeBin() || '✗ 未找到（npm install 未装全且 PATH 无 claude）'}  ·  登录 ${a.loggedIn ? '✓ ' + a.authMethod : '✗ 未登录（先跑 claude /login）'}`);
  const ov = detectedOverrides(); if (ov.length) console.log(`⚠ 检测到 ${ov.join(', ')}${STRIP_ENV ? '（已剥离，走官方登录）' : '（原样传给运行时；设 PRD_STRIP_ANTHROPIC_ENV=1 可剥离）'}`);
});
