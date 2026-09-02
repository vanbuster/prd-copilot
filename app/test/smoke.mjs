// 冒烟测试：不需要模型/登录，只测 HTTP 面（状态、文件面、参数校验、路径穿越拦截）
// 用法: node test/smoke.mjs
import { spawn } from 'node:child_process';
import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path';
const PORT = 4899;
const work = fs.mkdtempSync(path.join(os.tmpdir(), 'prdc-'));
fs.mkdirSync(path.join(work, 'prds'));
fs.writeFileSync(path.join(work, 'prds', '2026-01-01_demo_v1.md'), '---\ntitle: demo\n---\n# demo\n');
fs.writeFileSync(path.join(work, 'secret.txt'), 'nope');
const srv = spawn(process.execPath, ['server.mjs'], { cwd: path.resolve(new URL('..', import.meta.url).pathname), env: { ...process.env, PORT: String(PORT), PRD_WORKDIR: work }, stdio: ['ignore', 'pipe', 'pipe'] });
let fails = 0; const t = (ok, msg) => { console.log((ok ? 'PASS ' : 'FAIL ') + msg); if (!ok) fails++; };
const base = `http://127.0.0.1:${PORT}`;
let err = ''; srv.stderr.on('data', d => err += d); srv.stdout.on('data', () => {});
// 等端口就绪（最多 8s）
for (let i = 0; i < 40; i++) { try { await fetch(`http://127.0.0.1:${PORT}/api/files`); break; } catch { await new Promise(r => setTimeout(r, 200)); } }
try {
  const st = await (await fetch(`${base}/api/status`)).json();
  t(typeof st.loggedIn === 'boolean' && st.workdir === work, `/api/status 形状正确（loggedIn=${st.loggedIn}）`);
  const files = await (await fetch(`${base}/api/files`)).json();
  t(Array.isArray(files) && files[0]?.name === '2026-01-01_demo_v1.md', '/api/files 列出 prds/*.md');
  t((await fetch(`${base}/api/file?name=2026-01-01_demo_v1.md`)).status === 200, '/api/file 读取正常文件');
  t((await fetch(`${base}/api/file?name=../secret.txt`)).status === 404, '/api/file 拦截路径穿越');
  t((await fetch(`${base}/api/file?name=..%2Fsecret.txt`)).status === 404, '/api/file 拦截编码穿越');
  t((await fetch(`${base}/api/chat`, { method: 'POST', body: '{}', headers: { 'Content-Type': 'application/json' } })).status === 400, 'POST /api/chat 缺 text → 400');
  t((await fetch(`${base}/api/answer`, { method: 'POST', body: JSON.stringify({ requestId: 'nope' }), headers: { 'Content-Type': 'application/json' } })).status === 404, 'POST /api/answer 无待答问题 → 404');
  const html = await (await fetch(`${base}/`)).text();
  t(html.includes('PRD Copilot') && html.includes('/api/events'), 'GET / 返回控制台页面');
} catch (e) { t(false, '请求异常：' + e.message + (err ? '\n服务端 stderr: ' + err.slice(0, 400) : '')); }
srv.kill(); fs.rmSync(work, { recursive: true, force: true });
console.log(fails ? `SMOKE: ${fails} FAIL` : 'SMOKE: ALL PASS'); process.exit(fails ? 1 : 0);
