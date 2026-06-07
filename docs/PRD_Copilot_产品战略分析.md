# PRD Copilot — 产品战略分析

> 从笔试项目到可商业化的产品：全盘分析与架构重设计
> 版本：V1.0 | 2026-06-05

---

## 一、市场判断：赛道值得做吗？

### 1.1 市场规模

| 市场 | 2025 规模 | 2030+ 预测 | CAGR |
|------|----------|-----------|------|
| PM 软件市场 | $8.4B | $22.7B (2034) | 11.6% |
| AI 写作助手 | $3.3B | $24.8B (2035) | 25% |
| AI Agent 市场 | $7.9B | $294.7B (2035) | 43.7% |

**结论：赛道足够大，且处于爆发早期。** PM 软件是成熟市场，但 AI 原生的 PM 工具才刚刚出现。当前没有任何一个产品真正占据了「AI PRD 生成」这个品类的用户心智。

### 1.2 竞争格局

```
                    功能深度
                      ↑
           Productboard  Aha!
              ● $59/seat    ● $59/seat
              (PM全流程)     (路线图强)
                      |
                      |
         ChatPRD ●    |              ← 我们要占据的位置
         $15/mo        |
         (PRD聊天)     |
                      |
    Keeborg ●         |         Linear
    (开发者spec)       |         $10/seat
                      |
    FreePRD ●         |         Notion AI
    RockNRoll ●       |         $20/seat
                      |
                      └──────────────────→ 集成广度
```

**关键判断：市场存在一个明显的空白地带——「有深度的 PRD 生成 + 轻量集成」。**

- ChatPRD 占据了「便宜好用」但深度不足
- Productboard/Aha 深度够但贵且重
- Linear/Notion 广度够但 PRD 不是核心
- 没有任何产品做好 PRD → 工程交付的结构化衔接

### 1.3 我们的不对称优势

| 维度 | 我们的判断 |
|------|-----------|
| **时机** | ChatPRD 仅六位数 MRR、5 万用户。品类领导者的规模说明市场还未被教育完成，窗口期在 12-18 个月 |
| **中国本土化** | 所有竞品均为英文优先，无中文 PRD 框架适配。中国 PM 市场（300 万+从业者）几乎无本土 AI PRD 工具 |
| **PRD→工程衔接** | Keeborg 做了但面向开发者，ChatPRD 完全没做。这是最大的结构性空白 |
| **AI 原生** | 我们从 Day 1 就是 AI-native，不需要在传统 PM 工具上补 AI 能力 |

---

## 二、产品愿景

### 2.1 一句话定位

**PRD Copilot 是 PM 的 AI 结对编程伙伴——从模糊想法到可交付的产品文档，全程陪伴、自动补全、质量把关。**

### 2.2 三年愿景

| 阶段 | 时间 | 目标 | 北极星指标 |
|------|------|------|-----------|
| V1 — 验证期 | 0-6 月 | 上线 SaaS 版本，验证 PM 付费意愿 | 1000 注册用户，50 付费 |
| V2 — 成长期 | 6-18 月 | 建立 PRD→工程交付的差异化闭环 | 100 付费团队，NPS > 40 |
| V3 — 平台期 | 18-36 月 | 成为 PM 工作流枢纽，开放插件生态 | 500 团队，ARR $500K |

### 2.3 核心差异化策略

不做「又一个 ChatPRD」，而是做 **PM 到工程的桥梁**：

```
用户想法 → 澄清补全 → PRD 生成 → 协作评审 → 工程交付
   ↑          ↑           ↑          ↑          ↑
  当前已做    当前已做    当前已做    V2 新增    V2 新增
```

**为什么是 PRD→工程？** 因为 PM 最大的痛点不是「写 PRD」，而是「PRD 写了没人看、看了理解不一致、理解了实现又走样」。如果 PRD Copilot 能生成结构化的 spec，直接推送到 Linear/Jira/飞书项目，并且工程师可以基于这份 spec 开始编码——这才是完整的闭环。

---

## 三、用户画像

### 3.1 核心用户群

**画像 A：独立 PM / 创业者（个人版）**

| 属性 | 内容 |
|------|------|
| 代表 | 「我要做一个 AI 学习助手，帮我写份 PRD」 |
| 痛点 | 从 0 到 1 不知道 PRD 该写什么、格式不规范 |
| 付费意愿 | 低（$5-15/月），但对免费版容忍度高 |
| 获取渠道 | Product Hunt、小红书、即刻、PM 社群 |
| LTV | $60-180/年 |

**画像 B：中小团队 PM（团队版）**

| 属性 | 内容 |
|------|------|
| 代表 | 「团队要做一个新功能，需要快速出 PRD 并对齐」 |
| 痛点 | PRD 格式不统一、评审低效、工程交付断层 |
| 付费意愿 | 中（$15-30/seat/月），需团队价值论证 |
| 获取渠道 | 飞书/钉钉应用市场、PM 培训机构合作 |
| LTV | $1,800-3,600/团队/年 |

**画像 C：企业 PM 团队（企业版）**

| 属性 | 内容 |
|------|------|
| 代表 | 「我们需要标准化的 PRD 流程和 AI 辅助，集成到现有工作流」 |
| 痛点 | PRD 质量参差不齐、知识无沉淀、合规/安全要求 |
| 付费意愿 | 高（$50+/seat/月），但销售周期长 |
| 获取渠道 | 行业会议、BD、口碑推荐 |
| LTV | $30,000+/团队/年 |

### 3.2 优先级策略

```
V1（0-6月）：画像 A 为主，画像 B 为辅
V2（6-18月）：画像 B 为主，画像 C 开始接触
V3（18-36月）：画像 C 为主，企业功能完善
```

**理由**：个人用户获取成本低、反馈快，适合验证产品假设。但真正的收入来自团队和企业。先从个人切入，打磨核心体验，再向上扩展。

---

## 四、产品路线图

### V1 — 核心体验（0-6 月）

> 目标：从 Streamlit 原型升级为可商用的 Web SaaS

#### 4.1.1 架构升级

| 模块 | 当前状态 | V1 目标 |
|------|---------|---------|
| 前端 | Streamlit（单页） | Next.js / React SPA |
| 后端 | 无（Streamlit 内嵌） | FastAPI + PostgreSQL |
| 用户系统 | 无 | 注册/登录/团队（OAuth） |
| 存储 | session_state（内存） | 数据库持久化 + 文件存储 |
| LLM 调用 | 同步阻塞 | 异步 + 流式输出 + 队列 |
| 部署 | 本地 streamlit run | Docker + Cloud（Vercel/Railway） |

#### 4.1.2 功能清单

**P0（必须有）：**

| 功能 | 说明 |
|------|------|
| 用户系统 | 邮箱注册 + GitHub/Google OAuth |
| PRD 工作区 | 仪表盘展示所有 PRD，支持搜索/筛选 |
| 5 步生成流程 | 保留当前核心流程，优化交互 |
| 多模型支持 | DeepSeek / OpenAI / Claude / 本地模型 |
| 流式输出 | PRD 生成时逐字流式展示（SSE） |
| 导出增强 | Markdown + PDF + DOCX + Notion 导入 |
| 中英双语 | 保留并完善 i18n |
| 模板系统 | 预设 3-5 个行业模板（SaaS/移动端/AI/电商/B2B） |

**P1（应该有）：**

| 功能 | 说明 |
|------|------|
| PRD 版本历史 | Git-like 版本对比和回滚 |
| AI 评审 | 模拟工程师/设计师视角对 PRD 进行评审 |
| Prompt 自定义 | 高级用户可编辑生成 Prompt |
| 竞品分析模块 | 接入搜索 API，自动生成竞品对比表 |
| 团队空间 | 共享 PRD 库 + 评论 |

**P2（可以有）：**

| 功能 | 说明 |
|------|------|
| PRD 质量评分 | 完整性/一致性/可执行性三维评分 |
| 埋点建议 | 基于功能需求自动生成数据埋点方案 |
| API 开放 | 允许第三方集成 PRD 生成能力 |

### V2 — 协作与交付（6-18 月）

#### 4.2.1 核心能力

**PRD → 工程交付闭环**

```
PRD 文档
    ↓ 自动解析
结构化 Spec（JSON）
    ↓ 一键推送
Linear / Jira / 飞书项目
    ↓ 任务拆分
工程师可执行的 Ticket 列表
```

这是最核心的差异化功能。具体实现：

1. **Spec 解析引擎** — 将 Markdown PRD 解析为结构化 JSON：
   ```json
   {
     "modules": [
       {
         "name": "用户注册",
         "features": [
           {
             "title": "邮箱注册",
             "priority": "P0",
             "acceptance_criteria": ["...", "..."],
             "estimated_effort": "2d"
           }
         ]
       }
     ]
   }
   ```

2. **集成适配器** — 推送到 Linear / Jira / 飞书项目：
   - 每个功能点 → 一个 Ticket
   - 验收标准 → Ticket 描述的 checklist
   - 优先级 → Ticket label
   - 模块分组 → Epic

3. **AI 编码 Spec** — 为 AI Coding Agent（Cursor/Copilot）生成可直接消费的上下文：
   - 技术架构推荐
   - API 设计草案
   - 数据模型建议

**协作评审**

| 功能 | 说明 |
|------|------|
| 多人实时协作 | 基于 CRDT（Yjs）的协同编辑 |
| 异步评审 | @提及 + 评论 + 审批流 |
| AI 角色模拟 | 模拟工程师/设计师/QA 视角给出评审意见 |
| 变更追踪 | PRD 修改 diff + 变更通知 |

**知识库**

| 功能 | 说明 |
|------|------|
| 产品知识图谱 | 从历史 PRD 中提取实体关系（用户、功能、指标） |
| 上下文注入 | 新 PRD 自动关联历史 PRD 的相关内容 |
| 术语库 | 团队统一的产品术语定义 |

### V3 — 平台与生态（18-36 月）

| 方向 | 内容 |
|------|------|
| 插件市场 | 第三方开发者可发布 PRD 模板、Prompt 插件、集成适配器 |
| 企业级功能 | SSO/SAML、私有化部署、审计日志、数据驻留 |
| AI 产品全生命周期 | 从 PRD 扩展到竞品分析、用户研究、路线图规划 |
| 国际化 | 英语、日语、韩语、东南亚语言覆盖 |
| 数据智能 | PRD 质量 benchmark、行业 PRD 数据库 |

---

## 五、技术架构重设计

### 5.1 从原型到产品的架构演进

```
当前（原型）                    V1（产品）                     V2（平台）
┌─────────────┐           ┌─────────────────┐          ┌──────────────────┐
│  Streamlit   │           │   Next.js SPA   │          │   Next.js SPA    │
│  (Python)    │           │   (React/TS)    │          │   (React/TS)     │
│  单体应用     │    →      │       ↕         │    →     │       ↕          │
│  session内存  │           │   FastAPI        │          │   FastAPI        │
│  同步LLM调用  │           │   (Python)       │          │   (微服务拆分)    │
│  无用户系统   │           │       ↕         │          │       ↕          │
└─────────────┘           │   PostgreSQL     │          │   PostgreSQL     │
                          │   Redis          │          │   Redis + S3     │
                          └─────────────────┘          │   Event Bus      │
                                                       └──────────────────┘
```

### 5.2 V1 架构设计

```
┌──────────────────────────────────────────────────────────────┐
│                        用户层                                  │
│  Next.js (React 19) + Tailwind + shadcn/ui                   │
│  ├─ 仪表盘（PRD 列表/搜索/筛选）                                │
│  ├─ 编辑器（Markdown 编辑 + AI 侧边栏）                         │
│  ├─ 生成流程（5步向导）                                        │
│  └─ 设置（模板/团队/集成）                                      │
└──────────────────────┬───────────────────────────────────────┘
                       │ REST + SSE
┌──────────────────────▼───────────────────────────────────────┐
│                      API 层 (FastAPI)                          │
│  ├─ /auth        — 用户认证（JWT + OAuth）                     │
│  ├─ /prds        — PRD CRUD + 版本管理                        │
│  ├─ /generate    — AI 生成（SSE 流式输出）                      │
│  ├─ /templates   — 模板管理                                    │
│  ├─ /exports     — 导出服务（MD/PDF/DOCX/Notion）              │
│  └─ /integrations — 第三方集成                                 │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                     服务层                                     │
│                                                                │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐    │
│  │ AI 编排服务  │  │ 文档引擎      │  │ 集成服务           │    │
│  │             │  │              │  │                   │    │
│  │ • Prompt 管理│  │ • PRD 解析   │  │ • Linear Adapter │    │
│  │ • 模型路由   │  │ • 模板渲染   │  │ • Jira Adapter   │    │
│  │ • 流式输出   │  │ • 版本 Diff  │  │ • 飞书 Adapter   │    │
│  │ • 质量检查   │  │ • 导出转换   │  │ • Notion Adapter │    │
│  └──────┬──────┘  └──────┬───────┘  └─────────┬─────────┘    │
│         │                │                     │               │
│  ┌──────▼────────────────▼─────────────────────▼─────────┐    │
│  │                    数据层                               │    │
│  │  PostgreSQL          Redis              S3/R2          │    │
│  │  • users             • 会话缓存          • 导出文件     │    │
│  │  • prds              • 速率限制          • 附件         │    │
│  │  • prd_versions      • 队列                            │    │
│  │  • templates                                            │    │
│  │  • teams                                                │    │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

### 5.3 关键架构决策

#### 5.3.1 前端：为什么从 Streamlit 迁移到 Next.js

| 维度 | Streamlit | Next.js |
|------|-----------|---------|
| 交互控制 | 有限（Python 驱动） | 完全控制（React） |
| 流式输出 | st.write_stream（有限） | 原生 SSE + 流式 UI |
| 协作编辑 | 不支持 | Yjs/CRDT 原生支持 |
| 移动端适配 | 差 | 完全响应式 |
| SEO/分享 | 不支持 | SSR/SSG |
| 离线能力 | 无 | PWA |
| 开发效率 | 极高（原型） | 中（需要写更多代码） |

**迁移策略**：不是一次性重写，而是渐进式替换。

```
Phase 1：保留 Streamlit 后端作为 API，Next.js 作为新前端
Phase 2：用 FastAPI 逐个替换 Streamlit 端点
Phase 3：完全移除 Streamlit 依赖
```

#### 5.3.2 AI 编排层设计

当前问题：LLM 调用散落在 `app.py` 各处，无法管理、测试、迭代。

V1 的 AI 编排层：

```python
# services/ai/orchestrator.py
class AIOrchestrator:
    """统一的 AI 调用编排"""

    def __init__(self):
        self.model_router = ModelRouter()
        self.prompt_registry = PromptRegistry()
        self.quality_checker = QualityChecker()

    async def clarify(self, user_input: str) -> list[Question]:
        prompt = self.prompt_registry.get("clarify", version="latest")
        model = self.model_router.route(task="clarify")  # → flash
        raw = await model.complete(prompt.render(user_input=user_input))
        return self._parse_questions(raw)

    async def generate(self, context: PRDContext) -> AsyncIterator[str]:
        prompt = self.prompt_registry.get("generate", version="latest")
        model = self.model_router.route(task="generate")  # → pro
        async for chunk in model.stream(prompt.render(**context.to_dict())):
            yield chunk

    async def refine(self, prd: PRD, section: str, instruction: str) -> str:
        ...

    async def review(self, prd: PRD, perspective: str) -> ReviewResult:
        """V2 新增：模拟不同角色评审 PRD"""
        ...
```

```python
# services/ai/model_router.py
class ModelRouter:
    """根据任务类型、成本、延迟路由到不同模型"""

    ROUTING_TABLE = {
        "clarify": {"primary": "deepseek-v4-flash", "fallback": "gpt-4o-mini"},
        "generate": {"primary": "deepseek-v4-pro", "fallback": "claude-sonnet-4-6"},
        "refine": {"primary": "deepseek-v4-pro", "fallback": "gpt-4o"},
        "review": {"primary": "deepseek-v4-flash", "fallback": "gpt-4o-mini"},
    }

    def route(self, task: str, budget: float = None, latency: str = None) -> Model:
        config = self.ROUTING_TABLE[task]
        model_name = config["primary"]
        if not self._is_available(model_name):
            model_name = config["fallback"]
        return self._get_model(model_name)
```

```python
# services/ai/prompt_registry.py
class PromptRegistry:
    """Prompt 版本管理 —— 像 CI/CD 一样管理 Prompt"""

    def get(self, name: str, version: str = "latest") -> PromptTemplate:
        # 从数据库读取，支持 A/B 测试和灰度发布
        ...

    def evaluate(self, name: str, test_cases: list) -> EvalReport:
        # 用 golden set 评估 Prompt 质量
        ...
```

#### 5.3.3 文档数据模型

当前问题：PRD 存为一段 Markdown 字符串，精修时用字符串 replace，脆弱且不可靠。

V1 的结构化存储：

```python
# models/prd.py
class PRD(Base):
    id: UUID
    title: str
    user_id: UUID
    team_id: UUID | None
    status: Literal["draft", "clarifying", "generating", "refining", "exported"]

    # 原始输入
    raw_input: str
    clarify_answers: dict[str, str]

    # 结构化内容
    sections: list[PRDSection]  # JSON 字段，PostgreSQL 原生支持

    # 元信息
    template_id: str
    is_ai_product: bool
    quality_score: float | None

    created_at: datetime
    updated_at: datetime


class PRDSection(Base):
    key: str              # "overview" | "users" | "stories" | ...
    title: str
    content: str          # Markdown 内容
    order: int
    version: int
    metadata: dict        # 模块特有数据（如指标表格的 JSON）
```

**好处**：
- 精修时直接操作 `sections[i].content`，不再用字符串 replace
- 版本对比可以精确到模块级别
- 质量评分可以逐模块打分
- 导出时可以灵活组合模块

#### 5.3.4 流式输出架构

```
浏览器                  API 层                    LLM
  │                       │                       │
  │  POST /generate       │                       │
  │──────────────────────>│                       │
  │                       │  stream completion    │
  │                       │──────────────────────>│
  │  SSE: {"section":"overview","chunk":"## 1."}  │
  │<──────────────────────│                       │
  │  SSE: {"section":"overview","chunk":"产品"}   │
  │<──────────────────────│                       │
  │  ...                  │  ...                  │
  │  SSE: {"done":true}   │                       │
  │<──────────────────────│                       │
```

```python
# routers/generate.py
@router.post("/generate")
async def generate_prd(request: GenerateRequest):
    async def event_stream():
        context = await build_context(request)
        async for chunk in orchestrator.generate(context):
            # 逐段识别当前生成的模块
            event = parse_streaming_chunk(chunk)
            yield f"data: {event.json()}\n\n"

            # 同时写入数据库
            if event.section_complete:
                await save_section(request.prd_id, event.section_key, event.content)

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

---

## 六、商业模式

### 6.1 定价策略

| 层级 | 价格 | 功能 | 目标用户 |
|------|------|------|---------|
| **Free** | $0 | 3 份 PRD/月，基础模板，Markdown 导出 | 画像 A（试用） |
| **Pro** | $12/月 | 无限 PRD，全模板，多模型，PDF/DOCX/Notion 导出，版本历史 | 画像 A（付费转化） |
| **Team** | $25/seat/月 | Pro 全部 + 团队空间，协作评审，Linear/Jira/飞书集成，Spec 导出 | 画像 B |
| **Enterprise** | $50+/seat/月 | Team 全部 + SSO，私有化部署，审计日志，SLA，定制模板 | 画像 C |

### 6.2 收入模型

```
                    Year 1          Year 2          Year 3
Free 用户           5,000           30,000          100,000
Pro 用户 (5%)       250             1,500           5,000
Team 用户 (50团队)  500 seats       2,000 seats     10,000 seats
Enterprise (5家)    250 seats       1,000 seats     5,000 seats
                    ─────────       ─────────       ─────────
MRR                 $12K            $85K            $450K
ARR                 $144K           $1.02M          $5.4M
```

**关键假设**：
- Free → Pro 转化率 5%（ChatPRD 约为 3-5%）
- 团队平均 10 seats
- Enterprise 平均 50 seats

### 6.3 成本结构

| 成本项 | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| LLM API（最大变量） | $30K | $150K | $600K |
| 基础设施 | $5K | $20K | $80K |
| 人力（2-4 人） | $120K | $360K | $720K |
| 营销/获客 | $10K | $80K | $300K |
| **总计** | **$165K** | **$610K** | **$1.7M** |

**LLM 成本控制策略**：
1. 模型路由：澄清用 Flash（$0.1/M tokens），生成用 Pro（$2/M tokens）
2. 上下文压缩：历史 PRD 摘要后注入，而非全文
3. 缓存：相似问题的澄清结果缓存
4. Prompt 优化：减少不必要的 token 开销

---

## 七、当前代码到产品的差距分析

### 7.1 必须重构的部分

| 文件 | 当前问题 | 改造方向 |
|------|---------|---------|
| `app.py` (472 行) | 上帝文件，路由+状态+UI 全混在一起 | 拆分为路由层 + 服务层 + 数据层 |
| `utils/llm.py` | 同步调用、无流式、无错误处理 | 异步 + 流式 + 重试 + 降级 |
| `prompts/*.py` | Prompt 硬编码在 Python 文件中 | 移入数据库/文件，支持版本管理 |
| `static/style.css` | Streamlit 专属 CSS | 废弃，Next.js 用 Tailwind |
| 状态管理 | `session_state`（内存，刷新丢失） | 数据库持久化 |
| 导出 | 仅 Markdown | 增加 PDF/DOCX/Notion |

### 7.2 可以保留的部分

| 资产 | 说明 |
|------|------|
| Prompt 模板内容 | `system.py`/`clarify.py`/`generate.py`/`refine.py` 的文本质量已经很高，是核心资产 |
| 7+1 模块结构 | 经过市场验证的结构，直接复用 |
| 质量红线机制 | 独特的产品决策，保留并增强 |
| AI 产品检测逻辑 | 关键词列表可复用 |
| i18n 框架 | 翻译文本复用，切换逻辑重写 |
| 澄清问题设计 | 单选/多选自动判断的设计是好的，保留逻辑 |

### 7.3 V1 技术选型

| 层级 | 选型 | 理由 |
|------|------|------|
| 前端 | Next.js 15 + React 19 + Tailwind + shadcn/ui | 社区大、AI 编辑器友好、SSR |
| 后端 | FastAPI + Python 3.12 | 与现有 Prompt 资产兼容，异步原生 |
| 数据库 | PostgreSQL 16 | JSON 原生支持、成熟稳定 |
| 缓存 | Redis 7 | 会话缓存、速率限制、队列 |
| 文件存储 | Cloudflare R2 | S3 兼容、无出站流量费 |
| 部署 | Vercel（前端）+ Railway/Fly.io（后端） | 快速启动、按需扩缩 |
| LLM | DeepSeek（主）+ OpenAI（备）+ Anthropic（备） | 多模型路由降低风险 |

---

## 八、关键风险与应对

| 风险 | 严重性 | 应对策略 |
|------|--------|---------|
| ChatPRD 先发优势太大 | 中 | 差异化（PRD→工程衔接 + 中国市场）而非正面竞争 |
| LLM 生成的 PRD 质量不稳定 | 高 | 多层质量检查 + LLM-as-judge + 人工反馈循环 |
| LLM API 成本失控 | 高 | 模型路由 + 缓存 + Prompt 压缩 + Token 预算 |
| 用户留存低（工具型产品天然风险） | 高 | 从「工具」升级为「工作流」：工作区 + 模板 + 知识沉淀 |
| 大厂入局（Notion AI / Linear 增加 PRD 功能） | 中 | 深度 > 广度。专注于 PRD 质量和工程交付，不做泛 PM 工具 |
| Prompt 被轻易复制 | 低 | Prompt 只是产品的一部分，真正的壁垒在工作流和数据飞轮 |

---

## 九、前 90 天执行计划

### Month 1：技术地基

| 周 | 任务 | 交付物 |
|---|------|--------|
| W1 | 确定技术栈、搭建项目骨架 | Next.js + FastAPI + PostgreSQL 脚手架 |
| W2 | 用户系统（注册/登录/OAuth） | 可用的 auth 流程 |
| W3 | 迁移 AI 编排层（Prompt 管理 + 模型路由 + 流式） | AI 服务 API |
| W4 | PRD 数据模型 + CRUD | PRD 列表/创建/编辑/删除 |

### Month 2：核心体验

| 周 | 任务 | 交付物 |
|---|------|--------|
| W5 | 5 步生成流程前端 | 向导式 UI |
| W6 | 澄清问题交互 + PRD 编辑器 | 核心交互闭环 |
| W7 | 模板系统 + 导出服务 | 5 个预设模板 + MD/PDF/DOCX |
| W8 | 中英双语 + 移动端适配 | i18n + 响应式 |

### Month 3：上线准备

| 周 | 任务 | 交付物 |
|---|------|--------|
| W9 | 付费系统（Stripe 集成） | Free/Pro 付费墙 |
| W10 | 安全审计 + 性能优化 + 监控 | 安全报告 + 监控面板 |
| W11 | 内测（10-20 个 PM） | 反馈收集 + 快速修复 |
| W12 | Product Hunt 发布 + 中文社区推广 | 上线 |

---

## 十、总结

### 为什么做这个产品？

1. **市场空白真实存在**：PRD → 工程交付的衔接无人做好
2. **中国本土化是护城河**：300 万中文 PM 没有好用的 AI PRD 工具
3. **AI 原生时机对**：LLM 能力刚到生成高质量 PRD 的门槛
4. **个人能力匹配**：产品判断 + AI 应用开发 + 中英双语

### 不做什么？

- **不做泛 PM 工具**（路线图、需求池、迭代管理）——那是 Productboard/Aha 的战场
- **不做 AI Coding**——那是 Cursor/Copilot 的战场
- **不做项目管理**——那是 Linear/Jira 的战场
- **只做一件事：让 PM 产出高质量的、可交付的产品需求文档**

### 一句话

> PRD Copilot 不是帮你写文档的工具，是帮你思考清楚「做什么」和「为什么做」的 AI 伙伴。
