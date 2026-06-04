# PRD Copilot

> 一句话描述你的产品想法，AI 帮你生成结构化的 PRD 大纲。

PRD Copilot 是一个基于 LLM 的产品需求文档生成工具。通过多轮对话引导，将模糊的产品想法转化为可执行的 PRD。

## 功能特性

- **智能澄清** — 分析用户输入中的缺失信息，生成针对性的多选/单选问题
- **7+1 PRD 结构** — 产品概述、目标用户、用户故事、功能需求、非功能需求、信息架构、评估指标，AI 产品额外增加 AI 专项模块
- **逐节精修** — 生成后可选择任意模块进行展开补充
- **质量红线** — 禁止空洞表述（如"优化体验""提升性能"），所有指标必须量化
- **中英双语** — 一键切换中文/英文界面
- **Markdown 导出** — 一键导出标准 Markdown 格式 PRD 文档

## 快速开始

### 环境要求

- Python 3.10+
- DeepSeek API Key（或 OpenAI 兼容 API）

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/prd-copilot.git
cd prd-copilot

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 API Key

# 4. 启动应用
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`。

### 配置说明

编辑 `.env` 文件：

```env
# DeepSeek API（默认）
DEEPSEEK_API_KEY=your_key_here

# 也可切换为 OpenAI 或其他兼容 API
# OPENAI_API_KEY=your_key_here
# OPENAI_BASE_URL=https://api.openai.com/v1

# 模型选择（可选，默认使用下方配置）
MODEL_FAST=deepseek-v4-flash   # 用于需求澄清（快速响应）
MODEL_PRO=deepseek-v4-pro      # 用于 PRD 生成和精修（高质量）
```

## 交互流程

```
描述需求 → 澄清细节 → 生成 PRD → 精修内容 → 导出文档
```

1. **描述需求** — 用一句话或多句话描述你的产品想法
2. **澄清细节** — AI 生成 3-5 个关键问题，帮助你补全信息
3. **生成 PRD** — 基于你的输入和回答，生成完整的 PRD 大纲
4. **精修内容** — 选择任意模块展开补充，迭代优化
5. **导出文档** — 下载 Markdown 格式的 PRD 文件

## 项目结构

```
prd-copilot/
├── app.py                  # 主应用入口（Streamlit）
├── prompts/
│   ├── system.py           # 系统提示词（PM 角色定义）
│   ├── clarify.py          # 澄清问题生成提示词
│   ├── generate.py         # PRD 生成提示词
│   └── refine.py           # PRD 精修提示词
├── templates/
│   └── prd_template.py     # PRD 模块定义 + AI 产品检测
├── utils/
│   ├── llm.py              # LLM 客户端（OpenAI SDK 兼容）
│   └── export.py           # PRD 导出工具
├── static/
│   └── style.css           # 自定义样式
├── .env.example            # 环境变量模板
├── requirements.txt        # Python 依赖
└── README.md
```

## 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| Web 框架 | Streamlit | 开箱即用的 Python Web UI |
| LLM SDK | OpenAI Python SDK | 兼容 DeepSeek / OpenAI 等 API |
| 默认模型 | DeepSeek V4 | Flash 用于澄清，Pro 用于生成 |
| 前端样式 | 自定义 CSS | 深蓝 + 青绿配色体系 |

## 设计思路

### PRD 7+1 模块结构

参考 OpenAI PM Lead Miqdad Jaffer 的 AI PRD 模板和 ChatPRD 的模板库，精简为 7 个核心模块。当检测到用户描述涉及 AI/智能功能时，自动激活第 8 个「AI 专项」模块，涵盖模型能力边界、Prompt 策略、准确率指标和降级方案。

### 模型分层策略

- **Flash 模型**用于需求澄清 — 该任务需要快速响应，对创造性要求较低
- **Pro 模型**用于 PRD 生成和精修 — 需要更强的推理能力和输出质量

### 质量控制

通过系统提示词中的「质量红线」机制，确保生成的 PRD 不包含空洞表述。所有非功能需求必须包含量化指标，用户故事必须遵循 As a / I want / So that 三段式。

## 参考资料

| 来源 | 参考内容 |
|------|---------|
| [MetaGPT](https://github.com/FoundationAgents/MetaGPT) | 多角色 SOP 架构，PM Agent 的 PRD 生成流程 |
| [IBM MetaGPT 教程](https://www.ibm.com/cn-zh/think/tutorials/multi-agent-prd-ai-automation-metagpt-ollama-deepseek) | WritePRD/Review/Revise 的迭代精修模式 |
| [ChatPRD](https://www.chatprd.ai/) | PRD 模板分类体系（5 类 20+ 模板） |
| [OpenAI PM PRD 模板](https://www.productcompass.pm/p/ai-prd-template) | AI 产品 10 模块 PRD 结构 |
| [AI PRD vs 传统 PRD](https://www.woshipm.com/ai/6283143.html) | Model Story 概念，AI 产品 PRD 特殊性 |
| [GTPlanner](https://github.com/OpenSQZ/GTPlanner) | Context Engineering 思想 |
| [PRD-Taskmaster](https://github.com/anombyte93/prd-taskmaster) | 工程导向 PRD 设计 |

## License

MIT
