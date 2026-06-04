# PRD Copilot — 设计文档

> 本文档是项目实现的「源文档」。任何实现细节以此文档为准。
> 当上下文压缩导致实现方向偏离时，重新读取本文件即可恢复。

## 1. 项目背景

**来源**：DeepWisdom（赋智/MetaGPT 团队）AI 产品实习生笔试题。

**核心要求**：
- 用户输入自然语言产品需求描述 → 工具输出结构化 PRD 大纲
- 自行决定：PRD 模块定义、模糊输入处理、交互流程、输出格式
- 3 天内交付（实际 2-4 小时）
- 交付物：代码仓库 + README + 产品说明（500字）+ 演示截图 + 参考资料清单

**评分维度**：产品决策能力 > 代码工程化 > 功能完整性

## 2. 技术栈

| 组件 | 选择 | 理由 |
|------|------|------|
| 前端/应用层 | **Streamlit** | 内置聊天 UI + Markdown 渲染 + 文件下载，2-4h 可完成 |
| LLM | **DeepSeek API** (OpenAI 兼容) | 体现对 DeepWisdom 生态了解；成本低；可用 OpenAI SDK 调用 |
| 后端 | **Python 3.10+** | Streamlit 生态 + Prompt 工程天然契合 |
| 依赖 | openai, streamlit, python-dotenv | 最小依赖集 |

**为什么不选其他方案**：
- Next.js + React：开发时间超 4 小时
- Gradio：聊天 UI 不如 Streamlit 成熟
- LangGraph/LangChain：引入过重依赖，笔试题不需要

## 3. PRD 大纲结构（7+1 模块）

```
1. 产品概述 (Product Overview)
   - 背景与目标
   - 核心价值主张
   - 产品定位

2. 目标用户 (Target Users)
   - 用户画像（2-3 个典型用户）
   - 使用场景

3. 用户故事 (User Stories)
   - As a [角色], I want [需求], So that [价值]
   - 按优先级 P0/P1/P2 排列

4. 功能需求 (Functional Requirements)
   - 按模块分组
   - 每个功能含简述 + 验收标准
   - MoSCoW 优先级（Must/Should/Could/Won't）

5. 非功能需求 (Non-Functional Requirements)
   - 性能指标（量化）
   - 安全性
   - 可用性
   - 可扩展性

6. 信息架构 (Information Architecture)
   - 页面/模块结构
   - 核心交互流程（文字描述）
   - 状态流转

7. 评估指标 (Success Metrics)
   - 北极星指标
   - 关键业务指标（KPI）
   - 数据埋点需求

8. [AI 专项]* (AI Considerations) — 仅当检测到 AI 产品时补充
   - 模型能力边界
   - Prompt 设计策略
   - 准确率 / 幻觉率指标
   - 降级策略
```

**设计决策**：为什么是 7+1 而不是更多？
- 参考 OpenAI PM Lead 的 10 模块模板精简而来
- 2-4h 笔试题的 PRD 应「刚好够用」，过度设计反而不聚焦
- AI 专项是加分项——展示对 AI 产品 PRD 特殊性的理解

## 4. 交互流程（5 步多轮对话）

```
Step 1: 用户输入
  - 用户在聊天框输入自然语言产品描述
  - 最少 10 个字符，否则提示补充

Step 2: 澄清问题
  - Agent 分析用户输入，识别缺失信息
  - 生成 3-5 个关键问题（单选/简答混合）
  - 用户回答后进入下一步
  - 如果用户输入已经足够详细（Agent 判断），可跳过此步

Step 3: 生成 PRD 大纲
  - 基于用户输入 + 澄清回答，生成完整 7+1 模块 PRD
  - 以 Markdown 格式渲染展示
  - 每个模块以卡片形式呈现

Step 4: 逐节精修
  - 用户可点击选择某个模块
  - Agent 对该模块展开补充细节
  - 支持多轮精修直到用户满意

Step 5: 导出 PRD
  - 一键导出为 Markdown 文件
  - 包含完整的 7+1 模块内容
```

**设计决策**：为什么选多轮而非一次性？
- 参考 MetaGPT SOP 思想：分阶段流程比单次生成质量高
- 参考 Kuse 8 模板研究：有效 PRD 生成的首要原则是注入充分上下文
- Step 2 的澄清环节天然解决「模糊输入处理」这一考察点

## 5. 模糊输入处理策略

| 场景 | 策略 | 示例问题 |
|------|------|---------|
| 目标用户不清 | 补问用户画像 | "这个产品主要面向哪类用户？（如学生/职场人/企业）" |
| 功能边界模糊 | 提供选项引导 | "核心功能更偏向 A/B/C 中的哪个？" |
| 缺少上下文 | LLM 推断 + 确认 | "我理解这是一个面向...的产品，对吗？" |
| 输入过于笼统 | 拆分为子问题 | 将"做一个社交App"拆为人群、场景、差异化 |
| 完全不相关输入 | 引导重新描述 | "请描述一个你想做的产品或功能..." |

## 6. Prompt 工程架构

### 6.1 四层 Prompt 结构

```
Layer 1: System Prompt
  - 定义 Agent 角色：资深 AI 产品经理
  - 定义输出规范：Markdown 格式，严格遵循 7+1 模块
  - 定义质量标准：每个模块必须有实质性内容，不能空洞

Layer 2: PRD 模板上下文
  - 注入 7+1 模块的详细结构定义
  - 每个模块的字段说明和示例

Layer 3: 对话历史
  - 用户原始输入
  - 澄清问答记录

Layer 4: 任务指令
  - 澄清模式：分析缺失信息，生成问题
  - 生成模式：基于上下文生成完整 PRD
  - 精修模式：展开指定模块的细节
```

### 6.2 AI 产品检测逻辑

在澄清阶段，Agent 判断用户描述是否涉及 AI 功能（关键词匹配 + LLM 判断）：
- 触发词：AI、智能、模型、推荐、生成、识别、预测、Agent、Chatbot 等
- 如果检测到 AI 产品，PRD 自动包含第 8 模块（AI 专项）

## 7. 文件结构

```
prd-copilot/
├── DESIGN.md              ← 本文件（设计源文档）
├── app.py                 ← Streamlit 主入口（聊天 UI + 流程控制）
├── prompts/
│   ├── __init__.py
│   ├── system.py          ← System Prompt + 角色定义
│   ├── clarify.py         ← 澄清问题 Prompt
│   ├── generate.py        ← PRD 生成 Prompt
│   └── refine.py          ← 精修 Prompt
├── templates/
│   ├── __init__.py
│   └── prd_template.py    ← 7+1 模块定义 + 渲染逻辑
├── utils/
│   ├── __init__.py
│   ├── llm.py             ← LLM API 调用（OpenAI 兼容）
│   └── export.py          ← Markdown 导出
├── .env.example           ← API Key 模板
├── requirements.txt       ← Python 依赖
├── README.md              ← 运行说明 + 设计思路
└── PRODUCT.md             ← 产品说明（500字）
```

## 8. 核心实现要点

### 8.1 app.py 状态管理

使用 Streamlit session_state 管理多轮对话状态：

```python
# 状态定义
session_state = {
    "step": "input",           # input / clarify / generate / refine / export
    "user_input": "",          # 用户原始输入
    "clarify_questions": [],   # 澄清问题列表
    "clarify_answers": {},     # 用户回答
    "prd_content": "",         # 生成的 PRD Markdown
    "prd_sections": {},        # 各模块内容（用于精修）
    "is_ai_product": False,    # 是否 AI 产品
    "chat_history": [],        # 完整对话历史
}
```

### 8.2 LLM 调用封装

```python
# DeepSeek API（OpenAI SDK 兼容）
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
```

### 8.3 PRD 生成流程

1. 构造 System Prompt（角色 + 模板上下文）
2. 拼接对话历史（用户输入 + 澄清问答）
3. 添加生成指令
4. 调用 LLM，获取 Markdown 输出
5. 解析输出，按模块拆分存储
6. 渲染展示

## 9. 参考资料

| 来源 | 参考内容 |
|------|---------|
| [MetaGPT](https://github.com/FoundationAgents/MetaGPT) (68.5K stars) | 多角色 SOP 架构、PM Agent 的 PRD 生成流程 |
| [IBM MetaGPT 教程](https://www.ibm.com/cn-zh/think/tutorials/multi-agent-prd-ai-automation-metagpt-ollama-deepseek) | 5 Action + 3 Role 的具体代码实现、迭代精修模式 |
| [ChatPRD](https://www.chatprd.ai/) (100K+ users) | PRD 模板分类体系（5 类 20+ 模板）、多视角 Review |
| [OpenAI PM PRD 模板](https://www.productcompass.pm/p/ai-prd-template) | AI 产品 10 模块 PRD 结构（Miqdad Jaffer） |
| [AI PRD vs 传统 PRD](https://www.woshipm.com/ai/6283143.html) | Model Story 概念、AI 产品 PRD 的三个额外模块 |
| [墨刀 AI Agent](https://zhuanlan.zhihu.com/p/1966515812039893794) | 多轮对话 PRD 生成实践、三步法 |
| [Kuse PRD Prompt 模板](https://www.kuse.ai/blog/tutorials/ai-prd-prompt) | PRD 生成 Prompt 5 原则 + 8 模板 |
| [GTPlanner](https://github.com/OpenSQZ/GTPlanner) (287 stars) | Context Engineering、Prefab 组件化思想 |
| [PRD-Taskmaster](https://github.com/anombyte93/prd-taskmaster) (493 stars) | 工程导向 PRD、Claude Code Skill 分发 |

## 10. 开发计划

| 阶段 | 时间 | 内容 | 文件 |
|------|------|------|------|
| P1: 骨架 | 30min | 项目结构 + Streamlit 聊天 UI + API 调用 | app.py, utils/llm.py |
| P2: 核心 | 60min | Prompt 模板 + 多轮对话流程 + PRD 生成 | prompts/*.py, templates/ |
| P3: 体验 | 30min | 澄清问题 + 模块选择展开 + Markdown 导出 | app.py (UI), utils/export.py |
| P4: 打磨 | 30min | README + 产品说明 + 演示截图 | README.md, PRODUCT.md |
