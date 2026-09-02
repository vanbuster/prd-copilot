# app/ — 本地控制台（网页聊天壳）

一句话：在浏览器里和 prd-copilot 对话，不用开终端。**它不含任何提示词**——后端用 Claude Agent SDK
（Claude Code 的库形态）直接运行你装在 `~/.claude/skills/prd-copilot` 的同一个 skill，三道质量门、
独立评审子代理、落盘 `prds/` 全部原样。

```
浏览器（聊天 / 问题卡片 / 产出预览）
   ⇅ SSE + JSON
server.mjs（≈200 行，零框架，只用 node:http）
   ⇅ @anthropic-ai/claude-agent-sdk
Claude Code 运行时 → prd-copilot skill → prds/*.md
```

## 启动

```bash
cd prd-copilot/app && npm install     # 一次性；SDK 自带 Claude Code 运行时（约 200MB）
claude /login                         # 一次性；网页 OAuth，不需要 API key
npm start                             # → http://127.0.0.1:4870
```

产出默认落在**启动时所在目录**的 `prds/`，用 `PRD_WORKDIR=/path npm start` 指定；inbox 在该目录或其上一级自动发现。

## 环境变量

| 变量 | 作用 |
|---|---|
| `PORT` | 端口，默认 4870 |
| `PRD_WORKDIR` | 工作目录（产出 `prds/` 与 inbox 查找的根） |
| `PRD_MODEL` | 覆盖模型（默认跟随你的 Claude Code 设置） |
| `PRD_CLAUDE_BIN` | 指定 Claude Code 可执行文件（默认用 SDK 捆绑的） |
| `PRD_STRIP_ANTHROPIC_ENV=1` | 剥离 shell 里的 `ANTHROPIC_BASE_URL/AUTH_TOKEN/…`，强制走官方登录（用过第三方兼容端点的机器常有残留） |

## 它做什么 / 不做什么

- 做：流式显示回复；AskUserQuestion 的澄清问题渲染成卡片（可选项 / 自己写 / "你看着办"）；工具活动显示为一行摘要（门 1 扫描、写入、独立评审子代理…）；右栏列出 `prds/` 产出，点开预览、下载
- 不做：不托管到云端（只绑 127.0.0.1）；不存对话到自己的数据库（会话由 Claude Code 运行时持久化）；不复制 skill 的任何一行提示词进本目录

## 调试

页面顶栏显示登录态与工作目录；启动日志打印 skill 路径、运行时版本与检测到的 `ANTHROPIC_*` 覆盖。
skill 没被加载时，对话区会出现一条 `⚠ 本会话未加载到 prd-copilot skill`。
