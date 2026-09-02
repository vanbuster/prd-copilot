# Technical Architecture Patterns for AI-Powered Document Generation SaaS

> Research compiled: 2026-06-04
> Focus: Production-grade patterns for AI SaaS products that generate structured documents (PRDs, reports, contracts)

---

## Table of Contents

1. [Core Architecture Patterns](#1-core-architecture-patterns)
2. [Multi-Turn LLM Conversation Management](#2-multi-turn-llm-conversation-management)
3. [Document State Management](#3-document-state-management)
4. [Real-Time Collaboration](#4-real-time-collaboration)
5. [Typical Tech Stack (2026)](#5-typical-tech-stack-2026)
6. [Scaling: LLM Cost Management](#6-scaling-llm-cost-management)
7. [Scaling: Rate Limiting & Queue Management](#7-scaling-rate-limiting--queue-management)
8. [Scaling: Long-Running Generation Tasks](#8-scaling-long-running-generation-tasks)
9. [Integration Patterns](#9-integration-patterns)
10. [Prompt Versioning & Management](#10-prompt-versioning--management)
11. [AI Output Quality at Scale](#11-ai-output-quality-at-scale)
12. [What Leading AI SaaS Companies Do Differently in 2026](#12-what-leading-ai-saas-companies-do-differently-in-2026)

---

## 1. Core Architecture Patterns

AI-native SaaS products follow a layered architecture distinct from traditional SaaS:

### The Five-Layer Stack

```
┌─────────────────────────────────────┐
│  Product & API Layer                │  UI, APIs, webhooks, integrations
├─────────────────────────────────────┤
│  AI Orchestration Layer             │  Workflows, prompts, agents, tools
├─────────────────────────────────────┤
│  Model Access & Routing Layer       │  Multi-model routing, fallbacks, gateway
├─────────────────────────────────────┤
│  Data & Retrieval Layer             │  RAG, vectors, tenant-scoped knowledge
├─────────────────────────────────────┤
│  Platform Layer                     │  Auth, observability, metering, security
└─────────────────────────────────────┘
```

**Key distinction: AI-native vs AI-augmented:**
- **AI-augmented**: AI is a feature bolted onto existing product. Remove AI, product still works.
- **AI-native**: AI IS the product. Remove AI and the product has no value.

### Three Core AI Patterns

| Pattern | Purpose | Use Case |
|---------|---------|----------|
| **RAG** | Connect LLM to user-specific data | Knowledge base Q&A, document-aware generation |
| **Agents** | Execute multi-step workflows autonomously | End-to-end document creation, review cycles |
| **Embeddings** | Semantic search, classification, recommendations | Content matching, deduplication, similarity |

**For document generation specifically**, the primary pattern is **Agents** (multi-step document creation) with **RAG** as secondary (domain knowledge, templates, style guides).

### Multi-Tenancy Architecture

Shared across tenants:
- Model access layer and routing logic
- Prompt templates with tenant-level overrides
- Base orchestration runtime

Isolated per tenant:
- Retrieval indexes and vector databases
- Tool permissions and data connectors
- Evaluation datasets
- Agent memory and conversation history

**Critical**: Enforce quotas and rate limits at the AI gateway/orchestration layer (not just API edge). Scope retrieval by tenant. Set blast-radius limits for agent execution (max steps, tool calls, context size, retries).

---

## 2. Multi-Turn LLM Conversation Management

### The Core Challenge

LLMs degrade in multi-turn conversations. Research (ICLR 2025) confirms all evaluated models perform worse in multi-turn vs single-turn settings. Context accumulates, costs compound, and quality can drift.

### State Management Patterns

**Pattern 1: Conversation Thread + Message Store**
```
Conversation
  ├── id, tenant_id, user_id
  ├── metadata (title, tags, status)
  ├── created_at, updated_at
  └── Messages[]
       ├── id, role (system/user/assistant)
       ├── content (text or structured JSON)
       ├── token_count
       ├── model_used
       └── timestamp
```

Store every message in PostgreSQL. Track token counts per message for cost accounting. This is the baseline pattern.

**Pattern 2: Scratchpad / Working Memory**
Advanced agents use a "scratchpad" pattern -- a thinking space where the agent manages its own context internally before responding. The scratchpad is separate from the conversation visible to the user. This keeps user-facing conversation clean while allowing the agent to reason.

**Pattern 3: Chained Response IDs**
OpenAI's Response API supports `previous_response_id` for chaining multi-turn conversations server-side. This offloads context management to the provider but reduces your control.

**Pattern 4: Context Compaction**
Instead of sending full conversation history every turn, compact it:
- Traditional: Summarize older messages (risk: loses specifics like file paths, error codes)
- Modern: Verbatim deletion -- remove low-signal tokens (redundant formatting, verbose metadata) while keeping surviving content character-for-character identical. 50-70% token reduction with zero hallucination.

### Recommended Approach for Document Generation

```
For PRD/Report generation, use:
1. Structured conversation state in PostgreSQL
2. Document-level working memory (scratchpad) separate from chat
3. Context compaction on every turn (not just at context limit)
4. Track token counts per message for cost control
```

---

## 3. Document State Management

### The Document State Problem

AI-generated documents are not static text. They go through:
1. Initial generation (LLM produces structured output)
2. User edits (manual corrections, additions)
3. AI refinements (LLM revises specific sections)
4. Collaborative edits (multiple users)
5. Version history (track all changes)
6. Export (multiple formats)

### Pattern 1: JSON Document Model (Recommended for PRDs/Reports)

Store documents as structured JSON, not raw markdown:

```json
{
  "id": "doc-123",
  "type": "prd",
  "schema_version": "2.0",
  "metadata": {
    "title": "User Authentication Redesign",
    "author": "user-456",
    "status": "draft",
    "created_at": "2026-06-04T10:00:00Z",
    "updated_at": "2026-06-04T11:30:00Z"
  },
  "sections": [
    {
      "id": "sec-1",
      "type": "heading",
      "level": 1,
      "content": "Overview",
      "metadata": {"ai_generated": true, "model": "claude-sonnet-4"},
      "children": [
        {
          "id": "sec-1-1",
          "type": "paragraph",
          "content": "This document outlines...",
          "metadata": {"ai_generated": true, "edited_by_user": false}
        }
      ]
    }
  ]
}
```

**Benefits**: Section-level AI regeneration, granular edit tracking, structured export, template enforcement.

### Pattern 2: AST-Based (Editor-First)

For rich-text editors (ProseMirror, Lexical, TipTap), documents are stored as Abstract Syntax Trees. The editor's internal representation IS the document model.

```
Document AST
  ├── Paragraph nodes
  ├── Heading nodes  
  ├── List nodes
  ├── Custom block nodes (requirements table, acceptance criteria)
  └── Inline nodes (bold, links, mentions)
```

**Benefits**: WYSIWYG fidelity, editor-native, easy to merge concurrent edits.
**Trade-off**: Tied to editor library, harder to query/transform programmatically.

### Pattern 3: Hybrid (Best of Both Worlds)

Store a canonical JSON document model in PostgreSQL. Use TipTap/ProseMirror for editing with a bidirectional sync between editor AST and JSON model.

```
PostgreSQL (canonical JSON) <--> TipTap Editor (AST) <--> User
                              <--> AI Agent (JSON patches)
```

When AI generates or revises, it produces JSON patches to the document model, which are then applied to the editor. When users edit, changes flow back to update the JSON model.

---

## 4. Real-Time Collaboration

### CRDT vs OT

Two dominant algorithms for real-time collaborative editing:

| Aspect | OT (Operational Transform) | CRDT (Conflict-free Replicated Data Types) |
|--------|---------------------------|---------------------------------------------|
| **Used by** | Google Docs | Figma, Notion, many modern tools |
| **Server** | Requires central server for conflict resolution | Decentralized, auto-merges |
| **Offline** | Poor offline support | Excellent offline support |
| **Memory** | Lower memory overhead | Higher memory usage |
| **Complexity** | Complex server logic | Complex data structures |
| **Best for** | Centralized, always-online | Distributed, offline-capable |

**2026 recommendation: CRDT with Yjs**

### Yjs + AI Architecture

A cutting-edge pattern: treat the AI agent as a CRDT peer, not an external API caller.

```
User (browser) ←── Yjs CRDT ──→ Server (Yjs doc)
                                       ↑
AI Agent (server-side) ←── Yjs CRDT ──→
```

The AI agent writes directly into the shared Yjs document as a peer. This means:
- AI-generated content appears character-by-character (streaming)
- User can edit while AI is generating (no lock-out)
- Changes from both sides merge conflict-free
- Works offline

**Reference implementation**: [electric-sql/collaborative-ai-editor](https://github.com/electric-sql/collaborative-ai-editor) uses Yjs + y-prosemirror + Durable Streams.

### Practical Architecture for PRD Copilot

```
┌──────────────┐     WebSocket      ┌──────────────────┐
│  TipTap       │ ←──────────────→  │  Yjs Server      │
│  Editor       │                    │  (Hocuspocus)    │
│  (Browser)    │                    │                  │
└──────────────┘                    │  ┌────────────┐  │
                                    │  │ AI Agent   │  │
                                    │  │ (CRDT Peer)│  │
                                    │  └────────────┘  │
                                    └──────────────────┘
                                            │
                                    ┌───────┴────────┐
                                    │  PostgreSQL     │
                                    │  (persistent    │
                                    │   storage)      │
                                    └────────────────┘
```

---

## 5. Typical Tech Stack (2026)

Consensus from multiple sources on the recommended AI-native SaaS stack:

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Next.js 15 | Server components, streaming, edge runtime |
| **AI SDK** | Vercel AI SDK 4.x | Unified API for all providers, streaming, tool calling |
| **Editor** | TipTap / ProseMirror | Collaborative editing, extensible, Yjs bindings |
| **Database** | PostgreSQL + pgvector | One DB for relational + vector data |
| **Cache** | Redis / Upstash | Semantic caching, rate limiting, session state |
| **Queue** | Inngest / Trigger.dev | Background AI jobs, retries, observability |
| **CRDT** | Yjs + Hocuspocus | Real-time collaboration |
| **Auth** | Clerk / Auth.js | User management, org-level permissions |
| **Observability** | Langfuse / Helicone | LLM tracing, cost tracking, evaluation |
| **Deployment** | Vercel / AWS | Edge functions for API, containers for workers |

**Pro tip**: Use PostgreSQL with pgvector instead of a dedicated vector database until you hit 1M+ vectors. One fewer database to manage. HNSW indexing is fast enough for most SaaS workloads.

---

## 6. Scaling: LLM Cost Management

### The Cost Problem

LLM API costs compound in ways not obvious from pricing pages:
- A 2,000-token system prompt sent 200 times = 400K input tokens just for the repeated prompt
- A 20-turn conversation re-sends full history each time; early messages paid for 20 times
- A coding agent making 200 API calls on Claude Opus ($5/M input, $25/M output) = $20+ per session

### Five Levers for Cost Reduction (70-85% total)

**Lever 1: Model Routing (40-70% savings)**

Classify incoming requests by complexity, route to cheapest capable model:

| Complexity | % of Requests | Route To | Cost/1M Input |
|-----------|--------------|----------|---------------|
| Simple (classification, formatting) | 60% | GPT-4o-mini / Claude Haiku | $0.15-1.00 |
| Medium (summarization, Q&A) | 30% | Claude Sonnet / Gemini Pro | $1.25-3.00 |
| Complex (reasoning, code gen) | 10% | GPT-5.5 / Claude Opus | $2.50-5.00 |

Router classification costs ~$0.001/request, ~430ms latency. The ROI is enormous because 60-80% of requests are routine.

**Lever 2: Context Compaction (50-70% token reduction)**

Run compaction before every LLM call, not just at context window limit. Remove low-signal tokens while preserving specifics verbatim. A 200K conversation compacted to 80K saves 60% on input costs for that turn and every subsequent turn.

**Lever 3: Prompt Optimization (10-20% savings)**

- Audit system prompts: remove instructions the model follows by default
- Use 1-2 few-shot examples instead of 5
- Request structured JSON output instead of prose (saves 30-50% output tokens)
- Trim system prompt from 2000 to 800 tokens = $260K-$438K/year savings at scale

**Lever 4: Caching (60-90% savings on repeated content)**

Three levels:
1. **Provider-level**: Anthropic prompt caching (90% off on cache reads), OpenAI auto-caching (50% off)
2. **Application-level**: Redis cache keyed by prompt hash for identical queries
3. **Semantic caching**: Cache responses keyed by embedding similarity (>0.95 threshold). 30-50% LLM call reduction.

**Lever 5: Batching (50% flat discount)**

Both Anthropic and OpenAI offer batch APIs with 50% discount, 24-hour SLA. Use for: evaluation pipelines, bulk content generation, nightly reports, data labeling. Batch + cache = 95% savings on repeated prefixes.

### Cost Per User Benchmarks

| User Tier | Avg Requests/mo | AI Cost/User/mo | Target Price | Gross Margin |
|-----------|----------------|-----------------|-------------|-------------|
| Free | 50 | $0.50-2.00 | $0 | -100% (loss leader) |
| Starter | 500 | $3-8 | $29/mo | 72-90% |
| Pro | 2,000 | $10-25 | $79/mo | 68-87% |
| Enterprise | 10,000+ | $50-150 | $299+/mo | 50-83% |

**Target 70%+ gross margin on AI costs. Below 60% = need optimization.**

---

## 7. Scaling: Rate Limiting & Queue Management

### Why Traditional Rate Limiting Fails for LLMs

Traditional per-request rate limiting is insufficient because:
- One LLM request might use 200 tokens, another 200,000 tokens
- A 10-second generation uses the same "1 request" quota as a 0.5-second classification
- Multiple AI agents sharing a single API quota need coordination

### Token-Based Rate Limiting

Instead of requests/minute, use tokens/minute:

```
Rate Limit = max(tokens_per_minute, requests_per_minute)

Free:    10K tokens/min, 10 req/min
Pro:     100K tokens/min, 60 req/min  
Enterprise: 500K tokens/min, 200 req/min
```

Implementation: Redis sliding window counters tracking both tokens consumed and request count.

### AI Gateway Pattern

Place an AI gateway between your application and LLM providers:

```
App → AI Gateway → OpenAI
                  → Anthropic
                  → Google
```

Gateway handles:
- **Rate limiting**: Per-user, per-tenant, per-tier
- **Provider failover**: Auto-switch on 429/500 errors
- **Virtual keys**: Map user credentials to provider API keys
- **Usage tracking**: Per-feature, per-user cost attribution

**Tools**: Portkey, Kong AI Gateway, Truefoundry, or build your own with Vercel AI SDK.

### Queue Management for LLM Tasks

Use durable task queues (Inngest, Trigger.dev) for:
- Background document embedding
- Batch analysis jobs
- Report generation
- Retry on rate limit errors

```
User Request → API Server → Queue (Inngest)
                              ├── Worker 1: Process with LLM
                              ├── Worker 2: Process with LLM  
                              └── Worker 3: Process with LLM
                              
                              Auto-retry on rate limits
                              Observability built-in
```

### Multi-Agent Rate Limit Reconciliation

When multiple AI agents share a single API quota, use a **reconciliation loop** pattern:
1. Each agent checks remaining quota before making calls
2. Central coordinator allocates budget per agent
3. Agents report usage back after completion
4. Coordinator rebalances allocation based on priority

---

## 8. Scaling: Long-Running Generation Tasks

### The Problem

Document generation can take 30-120 seconds for complex PRDs. Users can't stare at a loading spinner that long.

### Architecture: SSE + Task Queue

```
┌────────┐  POST /generate   ┌──────────┐  Enqueue   ┌─────────┐
│ Client  │ ──────────────→  │ API       │ ────────→  │ Queue   │
│         │                   │ Server    │            │(Inngest)│
│         │  SSE connection   └──────────┘            └────┬────┘
│         │ ←──────────────                              │
│         │  stream: token, status,                      │
│         │  progress, complete                          ↓
│         │                                          ┌─────────┐
│         │                                          │ Worker   │
│         │                                          │ (LLM     │
│         │                                          │  calls)  │
│         │                                          └─────────┘
└────────┘
```

**Event types for SSE stream:**
- `token`: Partial output (streaming text)
- `status`: Progress updates ("Generating section 3 of 8...")
- `section_complete`: A document section is ready
- `error`: Something went wrong
- `complete`: Full document ready

### Streaming Strategy for Document Generation

Unlike chat (stream character-by-character), document generation benefits from **section-level streaming**:

1. Agent plans document structure (all sections)
2. Generates section-by-section, streaming each
3. Client renders completed sections immediately
4. User can start reading/reviewing while generation continues

### Edge Cases to Handle

- **Generation fails mid-way**: Store partial document, allow user to regenerate from failure point
- **User navigates away**: Task continues server-side, notify when complete
- **Concurrent edits during generation**: CRDT merges AI output with user edits
- **Provider outage**: Fallback to alternate provider mid-generation

---

## 9. Integration Patterns

### API-First Design

Treat APIs as the primary product interface. Your web UI is just one client.

```
API Gateway
├── /api/v1/documents          (CRUD)
├── /api/v1/documents/:id/generate  (AI generation)
├── /api/v1/documents/:id/sections  (Section-level ops)
├── /api/v1/templates          (Template management)
├── /api/v1/webhooks           (Webhook management)
└── /api/v1/integrations       (Third-party connections)
```

**Design principles:**
- Every action available in the UI has an API endpoint
- Streaming responses via SSE for generation endpoints
- Idempotent operations with request IDs
- Rate limiting and auth on every endpoint

### Plugin/Ecosystem Approach

Learn from Notion and Linear's integration patterns:

**Notion's approach:**
- Rich REST API covering all data types
- Webhook-like system (via integrations)
- Third-party "connections" in settings
- Public API enables building entire products on top of Notion

**Linear's approach:**
- GraphQL API for flexible querying
- Webhooks for real-time event notifications
- OAuth2 for third-party app authorization
- API-first: Linear's own frontend uses the same API

**For PRD Copilot:**

```
Integration Layer:
├── REST API (primary)
├── Webhooks (document.created, document.updated, review.completed)
├── OAuth2 (third-party authorization)
├── SDK (JavaScript/Python client libraries)
└── MCP Server (Model Context Protocol for AI tool integration)
```

### Export Integrations

Essential exports for document generation tools:

| Format | Use Case | Implementation |
|--------|----------|---------------|
| Markdown | Developer tools, Git | Direct serialization from JSON model |
| PDF | Official documents, printing | Puppeteer/Playwright rendering |
| DOCX | Enterprise workflows | docx.js or python-docx |
| Notion | Knowledge management | Notion API |
| Jira/Linear | Issue tracking | Their respective APIs |
| Confluence | Enterprise wiki | Confluence REST API |

---

## 10. Prompt Versioning & Management

### Why Prompt Versioning Matters

When OpenAI updates GPT-4o or Anthropic releases a new Claude version, your product's quality can change overnight. Prompts are configuration, not code -- they need versioning, testing, and deployment pipelines.

### Production-Grade Prompt Management

**Semantic versioning for prompts:**
```
prd-generation-v2.3.1
├── Major: Fundamental prompt restructure
├── Minor: New section type, changed instructions  
└── Patch: Wording tweaks, example updates
```

**Prompt Registry**: Centralized storage (MLflow Prompt Registry, Agenta, LangWatch) that provides:
- Version history with rollback
- A/B testing between versions
- Performance metrics per version
- Deployment targets (staging, production)
- Team review and approval workflows

### Prompt Deployment Pipeline

```
Prompt Change → Automated Evaluation → Staging Deploy → Manual Review → Production Deploy
                      │                                                      │
                      ├── 50-100 golden examples                              ├── Canary (5% traffic)
                      ├── LLM-as-judge scoring                               ├── Monitor metrics
                      └── Quality gate (threshold)                           └── Full rollout
```

### Tools Comparison

| Tool | Strength | Best For |
|------|----------|----------|
| **MLflow Prompt Registry** | Open-source, integrates with ML pipeline | Teams already using MLflow |
| **LangWatch** | End-to-end prompt management + eval | Full prompt lifecycle |
| **PromptLayer** | Visual registry, Git-like versioning | Visual prompt management |
| **Langfuse** | Tracing + prompt management | Observability-first teams |
| **Braintrust** | Evaluation + versioning | Quality-focused teams |
| **Agenta** | Prompt registry + testing | Rapid iteration |

### Practical Pattern: Prompts as Config

```
/prompts/
├── prd-generation/
│   ├── system.md              # System prompt
│   ├── section-overview.md    # Section-specific prompts
│   ├── section-requirements.md
│   ├── section-acceptance-criteria.md
│   └── config.json            # Model, temperature, version metadata
├── prd-review/
│   ├── system.md
│   └── config.json
└── registry.json              # Version mapping, active versions
```

Deploy prompts via feature flags (LaunchDarkly pattern) to:
- Roll out gradually
- Rollback instantly
- A/B test prompt versions
- Target specific user segments

---

## 11. AI Output Quality at Scale

### The Evaluation Stack

**Three layers of quality assurance:**

**Layer 1: Automated Test Suites**
- Maintain 50-100 "golden examples" with expected outputs
- Run against every model update and prompt change
- Use LLM-as-judge (GPT-4o evaluating your output) for subjective quality
- Run evaluations in CI/CD as a deployment gate

**Layer 2: Production Monitoring**
- User feedback signals: thumbs up/down, edit tracking, regeneration rate
- Cost monitoring: AI cost per user, per feature, per model
- Latency monitoring: time-to-first-token, total generation time (P95 < 3s)
- Quality metrics: RAGAS for RAG, custom metrics for generation

**Layer 3: Continuous Evaluation Pipeline**
```
Production traffic → Sample 1-5% → Run eval pipeline → Dashboard + Alerts
                                       ├── Correctness score
                                       ├── Relevance score
                                       ├── Completeness check
                                       └── Safety/bias screening
```

### LLM-as-Judge Pattern

Use a strong model (GPT-4o, Claude Sonnet) to evaluate outputs of your production model:

```python
evaluation_prompt = """
You are evaluating a PRD section generated by an AI.
Rate on:
1. Completeness (1-5): Does it cover all required aspects?
2. Clarity (1-5): Is the language clear and professional?
3. Actionability (1-5): Can a developer act on this?
4. Accuracy (1-5): Is the technical content correct?

Generated section: {output}
Original requirements: {input}

Provide scores and justification.
"""
```

### Key Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| User edit rate | < 30% of AI output edited | > 50% |
| Regeneration rate | < 20% | > 35% |
| Thumbs up rate | > 70% | < 50% |
| Generation latency (TTFT) | < 1s | > 3s |
| Total generation time | < 30s for standard doc | > 60s |
| Cost per successful outcome | Varies by tier | Exceeds margin |

---

## 12. What Leading AI SaaS Companies Do Differently in 2026

### Shift from Prototypes to Production Platforms

The industry has moved past the "AI experiment" phase. 2026 priorities:
1. **Reliability over novelty**: AI that works consistently beats flashy demos
2. **Cost discipline**: Per-request AI costs are the new COGS, demanding architectural optimization
3. **Evaluation infrastructure**: Continuous quality monitoring is non-negotiable
4. **Agentic workflows**: Multi-step AI agents replacing simple prompt-response patterns

### Key Differentiators

**1. AI agents as first-class architecture components**
Not just API calls -- agents have budgets, timeouts, audit logs, and human-in-the-loop controls. Agent execution is treated like distributed systems: bounded by steps, tokens, runtime, and cost.

**2. Multi-model routing as default**
No production system uses a single model anymore. Intelligent routing based on task complexity, latency budget, and cost constraints is table stakes.

**3. Prompt management as engineering discipline**
Prompts are versioned, tested, deployed, and monitored like code. Changes go through CI/CD with automated quality gates. Feature flags control prompt rollouts.

**4. Cost observability at every layer**
Not just "how much did we spend on OpenAI?" but "what did this feature cost per customer per successful outcome?" Cost intelligence drives architecture decisions.

**5. Structured output over free-form text**
Leading tools request JSON, not prose. Structured output is cheaper (fewer tokens), more reliable (parseable), and more composable (can be transformed). Free-form text is reserved for user-facing display.

**6. Streaming as default UX**
Every AI interaction streams. Time-to-first-token is the key latency metric. Users see content appearing within 200-500ms, even if full generation takes 30s.

**7. Evaluation in CI/CD**
Every deployment triggers automated evaluation against golden examples. Quality regression = deployment blocked. This treats AI quality like test coverage.

### What NOT to Do (Common Pitfalls)

1. **Over-engineering early**: Don't build custom agent framework, vector DB, or eval pipeline before 100 paying users. Start simple.
2. **Flat-rate pricing only**: Heaviest 10% of users consume 60%+ of AI costs. Add usage-based components.
3. **Ignoring latency**: Users tolerate 1-2s for AI, not 10-15s. If agent chain takes 10+ seconds, rethink approach.
4. **No evaluation system**: Model updates can silently break quality. Without automated evals, you won't know until users complain.
5. **Trusting LLM output for authorization**: Never let LLM output control permissions. Always validate server-side.

---

## Appendix: Reference Architecture for PRD Copilot

Based on all patterns above, a recommended architecture:

```
┌─────────────────────────────────────────────────┐
│                    Frontend                       │
│  Next.js 15 + TipTap Editor + Yjs Client         │
│  ├── Document editor (collaborative)             │
│  ├── AI chat panel (multi-turn conversation)     │
│  ├── Template browser                            │
│  └── Export panel                                │
└────────────────────┬────────────────────────────┘
                     │ REST API + SSE + WebSocket
┌────────────────────┴────────────────────────────┐
│                  API Layer                        │
│  Next.js API Routes / Express                    │
│  ├── Auth (Clerk)                                │
│  ├── Rate Limiting (Redis)                       │
│  └── Request routing                             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────┐
│            AI Orchestration Layer                 │
│  ├── Prompt Manager (versioned prompts)          │
│  ├── Document Agent (multi-step generation)      │
│  ├── Review Agent (quality checks)               │
│  └── Conversation Manager (state, compaction)    │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────┐
│         Model Access & Routing Layer             │
│  AI Gateway / Vercel AI SDK                      │
│  ├── Model router (complexity → model)           │
│  ├── Provider failover                           │
│  ├── Semantic cache (Redis)                      │
│  └── Token metering                              │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────┐
│              Data Layer                           │
│  PostgreSQL + pgvector + Redis                   │
│  ├── Documents (JSON document model)             │
│  ├── Conversations + Messages                    │
│  ├── Templates                                   │
│  ├── Embeddings (pgvector, tenant-scoped)        │
│  └── Prompt versions                             │
└─────────────────────────────────────────────────┘

Background Workers (Inngest/Trigger.dev):
├── Document generation tasks
├── Embedding computation
├── Export generation (PDF, DOCX)
├── Evaluation pipelines
└── Webhook delivery
```

---

## Sources

- [AI-Native SaaS Architecture — CloudZero](https://www.cloudzero.com/blog/ai-native-saas-architecture/)
- [AI-Native SaaS Architecture 2026 — Lushbinary](https://lushbinary.com/blog/ai-native-saas-architecture-patterns-developer-guide/)
- [LLM Cost Optimization: 5 Levers — Morph](https://www.morphllm.com/llm-cost-optimization)
- [How to Build AI SaaS in 2026 — Articsledge](https://www.articsledge.com/post/build-ai-saas)
- [AI Agent Rate Limiting Strategies — Fast.io](https://fast.io/resources/ai-agent-rate-limiting/)
- [Rate Limiting for LLM Applications — Portkey](https://portkey.ai/blog/rate-limiting-for-llm-applications)
- [Token-Based Rate Limiting for AI Agents — Zuplo](https://zuplo.com/learning-center/token-based-rate-limiting-ai-agents)
- [Rate Limiting in AI Gateway — Truefoundry](https://www.truefoundry.com/blog/rate-limiting-in-llm-gateway)
- [9 AI Agents, One API Quota — Tamir Dresher](https://www.tamudresh.com/blog/2026/03/21/rate-limiting-multi-agent)
- [Streaming AI Agents with SSE — Medium](https://akanuragkumar.medium.com/streaming-ai-agents-responses-with-server-sent-events-sse-a-technical-case-study-f3ac855d0755)
- [AI Agents as CRDT Peers with Yjs — Electric](https://electric.ax/blog/2026/04/08/ai-agents-as-crdt-peers-with-yjs)
- [Collaborative AI Editor — Electric SQL GitHub](https://github.com/electric-sql/collaborative-ai-editor)
- [OT vs CRDT — TinyMCE](https://www.tiny.cloud/blog/real-time-collaboration-ot-vs-crdt/)
- [OT vs CRDT in 2026 — Taskade](https://taskade.com/blog/ot-vs-crdt)
- [Real-Time AI Editor with CRDTs — The Main Thread](https://www.the-main-thread.com/p/real-time-ai-editor-quarkus-crdt-langchain4j)
- [Prompt Versioning Guide — LaunchDarkly](https://launchdarkly.com/blog/prompt-versioning-and-management/)
- [Prompt Versioning Best Practices 2025 — Maxim AI](https://www.getmaxim.ai/articles/prompt-versioning-and-its-best-practices-2025/)
- [Prompt Registry — MLflow](https://mlflow.org/prompt-registry)
- [Prompt Management — LangWatch](https://langwatch.ai/blog/what-is-prompt-management-and-how-to-version-control-deploy-prompts-in-productions)
- [LLM Evaluation Metrics — Confident AI](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation)
- [LLM-as-Judge — Arize AI](https://arize.com/llm-evaluation/)
- [LLM Evaluation Framework — Evidently AI](https://www.evidentlyai.com/blog/llm-evaluation-framework)
- [LLM Evaluation Best Practices — Datadog](https://www.datadoghq.com/blog/llm-evaluation-framework-best-practices/)
- [Production LLM Evaluation Guide — W&B](https://wandb.ai/ai-team-articles/llm-evaluation/reports/Production-ready-LLM-evaluation-guide--VmlldzoxNTI5MjA2NA)
- [API-First Design — Contentful](https://www.contentful.com/blog/what-is-api-first/)
- [API-First for SaaS — Prismatic](https://prismatic.io/blog/api-first-to-unlock-scalablity-and-integrations/)
- [Multi-Turn Context Management — Medium](https://medium.com/@linz07m/multi-turn-context-management-navigating-the-long-conversation-de79b712bbf7)
- [LLMs Get Lost in Multi-Turn — ICLR](https://openreview.net/pdf?id=VKGTGGcwl6)
- [SaaS 2026 Trends — Ardas IT](https://ardas-it.com/saas-2026-trends-from-ai-experiments-to-production-ready-platforms)
