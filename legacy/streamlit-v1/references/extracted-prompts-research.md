# Extracted PRD Generation Prompts - Research Reference

> Extracted from GitHub on 2026-06-04 for prd-copilot prompt rewrite.
> This file contains the ACTUAL LLM prompts from each source.

---

## Source 1: Agentic PRD Generation (SeeknnDestroy/agentic-prd-generation)

**Architecture**: FastAPI + Streamlit, 4-step pipeline: Outline -> Draft -> Critique -> Revise (loop)
**Source file**: `backend/pipelines/prompts.py`

### OUTLINE_PROMPT
```
You are a world-class product manager. Your task is to create a structured
outline for a Product Requirements Document (PRD) based on a given project idea.

The outline should cover all standard sections of a PRD, including:
1.  Executive Summary
2.  Problem Statement & User Personas
3.  Goals & Success Metrics
4.  Functional Requirements (Features)
5.  Non-Functional Requirements (Performance, Security, etc.)
6.  Out-of-Scope Items
7.  Risks & Mitigations

Please generate a Markdown-formatted outline for the following project idea:

**Project Idea:** "{idea}"

**Instructions:**
- Use Markdown headings (`#`, `##`, `###`) to structure the document.
- For each section, include a brief, one-sentence placeholder description of
  what it will contain.
- Do NOT write the full content of the PRD yet. Just the outline.
```

### DRAFT_PROMPT
```
You are a world-class product manager. Your task is to expand a given PRD
outline into a full first draft.

Use the provided outline and flesh out each section with detailed, clear, and
concise content. Make reasonable assumptions where necessary, but clearly
state them.

**PRD Outline to Draft:**
```markdown
{outline}
```

**Instructions:**
- Write comprehensive content for every section of the outline.
- Use clear and professional language.
- Format the output as a complete Markdown document.
- Ensure the functional requirements are specific and actionable.
- The draft should be complete enough for a stakeholder to understand the
  entire scope of the project.
```

### CRITIQUE_PROMPT
```
You are a meticulous and critical product manager. Your task is to review a
draft of a Product Requirements Document (PRD) and provide constructive
feedback.

Analyze the following PRD draft for clarity, completeness, coherence, and
realism. Identify any ambiguities, contradictions, or missing information.

**PRD Draft to Critique:**
```markdown
{draft}
```

**Instructions:**
- Provide your critique as a list of bullet points.
- For each point, specify the section of the PRD it refers to.
- Focus on actionable feedback that can be used to improve the document.
- Be ruthless but fair. The goal is to make the PRD as strong as possible.
- **If the PRD is well-structured, clear, and comprehensive with no obvious issues, you MUST respond with the exact phrase "No issues found."**
- Do not add any other text or formatting if you are approving the document.
```

### REVISE_PROMPT
```
You are a world-class product manager. Your task is to revise a Product
Requirements Document (PRD) draft based on a set of critiques.

Carefully review the original draft and the provided feedback. Update the PRD
to address all the points raised in the critique.

**Original PRD Draft:**
```markdown
{draft}
```

**Critique to Address:**
```
{critique}
```

**Instructions:**
- Produce a new, complete version of the PRD in Markdown format.
- Incorporate all the suggested changes from the critique.
- Ensure the revised document is coherent and consistent.
- Do not include the critique in the final output. Only the revised PRD.
```

### Pipeline Logic
```python
MAX_REVISIONS = 3
APPROVAL_PHRASE = "No issues found."

# Pipeline stages: outline_step -> draft_step -> critique_and_revise_loop
# The critique-revise loop runs up to MAX_REVISIONS times
# If critique contains "No issues found.", the loop breaks early
```

**Key Insight**: The auto-approval mechanism via `APPROVAL_PHRASE = "No issues found."` is elegant -- it lets the LLM self-validate and stop iterating when quality is sufficient. The max 3 revisions prevents infinite loops.

---

## Source 2: AI-Native PM OS (vishalmdi/ai-native-pm-os, 84 stars)

**Architecture**: Claude Code Skill, 5-stage manual workflow: Seed -> Outline -> Draft -> Critique -> Polish
**Source file**: `module-3/3-1-prd-from-scratch.md`

### Stage 1: SEED (Feature Brief)
```
I'm going to write a PRD for Meridian's Conditional Approval Routing feature.
Before we start, let me give you the brief.

Feature: Conditional Approval Routing
Problem: Operations teams need workflows where the approval path changes 
based on attributes of the request — amount, department, requester role, 
or custom conditions. Currently all approvals go to the same person regardless 
of context, creating bottlenecks and misrouted requests.

Target user: Marcus (Operations Manager) — builds the workflow
End user: Asha (Finance Analyst) — submits requests through the workflow

Locked decisions (cannot change):
- Routing logic is condition-based (if/then), not ML-based
- Maximum chain depth: 8 levels
- Mobile approval UI is out of scope for v1
- OOO escalation: auto-escalate after 48 hours to manager

Open questions (to be resolved in PRD):
- Partial approvals: can a chain complete if 3/4 approvers approve?
- Audit trail depth: what level of detail do enterprise customers need?
- Notification cadence: how often to remind pending approvers?

Business context:
- This feature directly supports Q2 KR1 (reduce activation time) and KR4 (enterprise ARR)
- Competitor Zapier has basic approval routing but no conditional logic
- Three enterprise prospects have cited this feature as a blocker to signing

Read this brief carefully. Then confirm you understand it by summarizing 
the core problem, the target user, and the top open question in 2 sentences each.
Do not start drafting yet.
```

### Stage 2: OUTLINE (Structure First)
```
Based on the brief, propose an outline for this PRD.

Use this as your structural guide:
1. Overview (problem, solution hypothesis, why now)
2. User Context (primary user, secondary users, current behavior)
3. Goals & Success Metrics (primary metric, secondary metrics, guardrails)
4. What We're Building (feature description, key behaviors)
5. What We're NOT Building (explicit scope exclusions)
6. Open Questions & Decisions (your recommended answer for each)
7. Technical Considerations (constraints from locked decisions)
8. Launch Checklist (pre-launch dependencies)

For each section, note what the 2-3 most important things to cover are.
Do not write the PRD yet — just the outline with bullet points per section.
```

### Stage 3: DRAFT (Full PRD)
```
The outline looks good. Now write the full PRD.

Guidelines:
- Use the Meridian terminology from ABOUT-ME/CLAUDE.md (routing sequence, workflow nodes, etc.)
- For the Open Questions section, provide your recommended answer for each question,
  with brief rationale
- Write the "What We're NOT Building" section with at least 4 explicit exclusions
- Success metrics must be measurable and time-bound
- Write for a technical audience — engineers should be able to build from this

Save the draft to: CLAUDE-OUTPUTS/prds/approval-routing-prd-v1.md
```

### Stage 4: CRITIQUE (3-Perspective Review)
```
Read CLAUDE-OUTPUTS/prds/approval-routing-prd-v1.md.

Review it from three perspectives simultaneously:

ENGINEER CRITIQUE:
- What requirements are technically ambiguous?
- What edge cases aren't handled?
- What assumptions could cause a mid-sprint surprise?

DESIGNER CRITIQUE:
- What user flows are underspecified?
- Where might the UX create friction for Marcus or Asha?
- What user states (empty, error, loading) aren't addressed?

EXEC CRITIQUE (CEO lens):
- What's missing from the "why now" argument?
- Is the business impact clear and quantified?
- What would a competitor already have done here?

Return each critique as a numbered list under its header.
Save critique to: CLAUDE-OUTPUTS/prds/approval-routing-prd-v1-critique.md
```

### Stage 5: POLISH (Incorporate Critique)
```
Read:
- CLAUDE-OUTPUTS/prds/approval-routing-prd-v1.md (original draft)
- CLAUDE-OUTPUTS/prds/approval-routing-prd-v1-critique.md (critique)

Revise the PRD incorporating the highest-priority critique points.
For each change you make, add a brief inline note: [REVISED: reason]
so I can see what changed and why.

Prioritize:
1. Technical ambiguities (engineer critique)
2. Missing user states (designer critique)  
3. Business impact clarity (exec critique)

Save to: CLAUDE-OUTPUTS/prds/approval-routing-prd-v2.md
```

### PRD Template (Reusable)
```markdown
# PRD: [Feature Name]
**Author:** [Name] | **Date:** [Date] | **Status:** Draft / Review / Approved  
**Version:** v[N]

---

## 1. Overview

### Problem
[1-2 sentences: what pain exists and who feels it]

### Solution Hypothesis
[1-2 sentences: what we're building and why it solves the problem]

### Why Now
[What makes this the right moment: business context, competitive pressure, user demand]

---

## 2. User Context

### Primary User
**[Persona name]** — [role and company type]
Current behavior: [what they do today without this feature]
Desired outcome: [what success looks like for them]

### Secondary Users
[Other users affected by this feature]

---

## 3. Goals & Success Metrics

### Primary Metric
[One number that tells us if this feature worked]
Target: [X% improvement in Y within Z weeks of launch]

### Supporting Metrics
- [Metric 2]: [target]
- [Metric 3]: [target]

### Guardrail Metrics (must not degrade)
- [Metric]: [threshold]

---

## 4. What We're Building

### Feature Description
[Clear prose description of the feature]

### Key Behaviors
- [Behavior 1]
- [Behavior 2]
- [Edge case handling]

---

## 5. What We're NOT Building (v1)

- [Explicit exclusion 1]
- [Explicit exclusion 2]
- [Explicit exclusion 3]
- [Explicit exclusion 4]

---

## 6. Open Questions & Decisions

| Question | Recommended Answer | Rationale | Owner | Due |
|----------|-------------------|-----------|-------|-----|
| [Q1] | [A1] | [Why] | [Name] | [Date] |

---

## 7. Technical Considerations

[Constraints, locked decisions, dependencies]

---

## 8. Launch Checklist

- [ ] Engineering spec reviewed by Tara
- [ ] Design mockups approved
- [ ] Success metrics instrumented in Amplitude
- [ ] Documentation updated
- [ ] Sales enablement brief sent to Rohan
```

**Key Insight**: The 3-perspective critique (Engineer/Designer/Exec) is the standout pattern here. Most PRD prompts skip critique entirely or use a single generic reviewer. The multi-role approach catches different classes of problems.

---

## Source 3: GTPlanner (OpenSQZ/GTPlanner)

**Architecture**: Multi-tool agent with orchestrator -> short_planning -> prefab_recommend -> design pipeline
**Note**: GTPlanner generates Agent design documents (design.md), NOT traditional PRDs. However, its prompt architecture is highly sophisticated and many patterns transfer.

### System Orchestrator Prompt (Chinese - Full, ~500 lines)
See: `gtplanner/agent/prompts/templates/system/orchestrator.py`

Key architectural patterns from the orchestrator:
- **Intent Classification First**: Before calling any tool, classify whether user wants to "design" or is just "consulting"
- **Tool Chain Routing**: Different flows based on complexity:
  - Flow A: Standard (recommend -> list_functions -> design)
  - Flow B: Vague requirements (clarify -> recommend -> design)
  - Flow C: Complex (recommend -> planning -> design)
  - Flow D: Multi-prefab (multiple recommend calls -> design)
  - Flow E: Deep research (recommend -> research -> design)
  - Flow G: Non-design (no tools, direct dialogue)
- **Sequential Tool Calling**: Explicit prohibition on concurrent tool calls
- **Minimal Questioning Rule**: Max 2-3 clarifying questions before generating

### Short Planning Prompt (English)
```
# Role
You are a system architect focused on backend business logic and data processing design.

# Important Constraints
1. **Only plan backend logic**: Do not include frontend UI, interface, or user interaction
2. **File Handling Principles**: The API only receives S3 URL strings. **DO NOT plan** the following:
   - File upload/download steps
   - File format validation steps
   - Temporary file management steps
   - Directly use prefabs to process S3 URLs

# Core Task
Generate a clear, step-by-step backend implementation plan based on user requirements and available information.

# Input Information

1. **User Requirements:**
   ```
   {req_content}
   ```

2. **Recommended Prefabs List:**
   ```
   {prefabs_content}
   ```

3. **Technical Research Results:**
   ```
   {research_content}
   ```

# Output Specification

### Step-by-step Implementation Plan
- **Format**: Numbered step list (backend logic only)
- **Requirements**:
  * Each step describes a clear backend functional module or processing stage
  * Use backend business language (e.g., data reception -> validation -> processing -> storage -> return)
  * **If recommended prefabs are available, prioritize using them**
  * **If technical research results are available, incorporate optimizations**
  * Mark optional features: `(Optional)`
  * Identify parallel processing modules
```

### Design Prompt (English, key sections)
```
You are a professional System Architect, skilled at transforming user requirements into clear, high-level system design documents.

# Core Principles

1. **High-Level Abstraction**: Describe "what" the system does, not "how" it does it.
2. **No Implementation Details**: Do not include specific technical implementation details
3. **Logical Clarity**: Focus on the flow, data structures, and node responsibilities.
4. **Structured Output**: Strictly follow the specified document template.

# Output Format (Follow Strictly)

## Standard Operating Procedure
## Flow Design (with mermaid diagrams)
## Prefabs (tool integrations)
## Utility Functions
## Node Design (with Shared Store + Node Steps)
```

**Key Insight**: GTPlanner's orchestrator prompt demonstrates how to build a production-grade agent system prompt with:
1. Explicit intent classification before action
2. Multiple flow paths based on input complexity
3. Strict tool calling protocols (sequential, no concurrency)
4. Detailed positive/negative examples for each behavior

---

## Source 4: PRD-Taskmaster (anombyte93/prd-taskmaster)

**Architecture**: 12-step Claude Code Skill workflow with Taskmaster integration
**Note**: PRD-Taskmaster does NOT have a traditional system prompt. It's a workflow orchestration document (SKILL.md) that guides Claude through 12 steps. The actual "prompt" is the combination of the SKILL.md instructions + the comprehensive PRD template.

### Workflow Steps
1. **Preflight** - Check environment
2. **Detect Existing PRD** - Resume or restart
3. **Detect Taskmaster** - Check tool availability
4. **Discovery Questions** (13 questions) - Gather context
5. **Initialize Taskmaster** - Setup tracking
6. **Generate PRD** - Load template, AI fills it
7. **Validate PRD Quality** - 13 automated checks (EXCELLENT/GOOD/ACCEPTABLE/NEEDS_WORK)
8. **Parse & Expand Tasks** - Break into subtasks
9. **Insert User Test Tasks** - Add testing requirements
10. **Setup Tracking Scripts** - Configure progress tracking
11. **Generate CLAUDE.md** - Create project instructions
12. **Summary** - Final report

### Discovery Questions (Step 4)
The 13 discovery questions cover:
1. Product name and one-line description
2. Problem being solved
3. Target users and personas
4. Current workflow/process
5. Key pain points
6. Desired outcomes and success metrics
7. Core features (must-haves vs nice-to-haves)
8. Non-functional requirements
9. Technical constraints
10. Integration requirements
11. Timeline and milestones
12. Risks and concerns
13. Out-of-scope items

### Validation Checks (Step 7, 13 automated checks grading EXCELLENT/GOOD/ACCEPTABLE/NEEDS_WORK)
The PRD is graded on:
1. Executive Summary completeness
2. Problem Statement clarity
3. User Stories quality (As a/I want/So that format)
4. Functional Requirements specificity
5. Non-Functional Requirements measurability
6. Technical Considerations depth
7. Implementation Roadmap feasibility
8. Acceptance Criteria testability
9. Risk Assessment completeness
10. Success Metrics quantification
11. Scope Boundaries clarity
12. Dependency identification
13. Overall coherence and consistency

### PRD Template Structure (comprehensive, from templates/taskmaster-prd-comprehensive.md)
- Executive Summary
- Problem Statement (Current Situation, User Impact, Business Impact, Why Now)
- Goals & Success Metrics (with Baseline/Target/Timeframe/Measurement Method)
- User Stories (with Acceptance Criteria, Task Breakdown Hints, Dependencies)
- Functional Requirements (P0/P1/P2 with Technical Specifications, Task Breakdown)
- Non-Functional Requirements (Performance, Security, Scalability, Reliability, Accessibility, Compatibility)
- Technical Considerations (System Architecture, API Specifications, Database Schema, Technology Stack, External Dependencies, Migration Strategy, Testing Strategy)
- Implementation Roadmap (5 phases with task dependencies, effort estimation)
- Out of Scope
- Open Questions & Risks
- Validation Checkpoints
- Appendix: Task Breakdown Hints

**Key Insight**: PRD-Taskmaster's most valuable contribution is the **automated validation step** -- it grades the generated PRD against 13 quality dimensions. This is essentially a built-in quality gate that most other approaches lack. The grading rubric (EXCELLENT/GOOD/ACCEPTABLE/NEEDS_WORK) could be adapted into a Streamlit "quality score" feature.

---

## Cross-Source Pattern Analysis

### Common Patterns Across All Sources

| Pattern | Agentic PRD | AI-Native PM OS | GTPlanner | PRD-Taskmaster |
|---------|------------|-----------------|-----------|----------------|
| Multi-stage generation | Yes (4 stages) | Yes (5 stages) | Yes (multi-tool) | Yes (12 steps) |
| Separate outline from draft | Yes | Yes | Yes (short_planning -> design) | Implicit |
| Critique/review stage | Yes (auto-approve) | Yes (3-perspective) | N/A | Yes (13 checks) |
| Iterative refinement | Yes (max 3 loops) | Yes (inline notes) | Yes (edit_document) | Yes (quality grades) |
| Role-based prompts | Yes (PM persona) | Yes (PM/Eng/Design/Exec) | Yes (Architect) | Yes (PM + Validator) |
| Template-driven output | No (free-form) | Yes (8-section) | Yes (strict template) | Yes (comprehensive template) |
| Quality self-assessment | Yes (phrase check) | No | No | Yes (13-dimension grading) |

### Recommended Architecture for prd-copilot Rewrite

Based on the analysis, the recommended prompt architecture for a Streamlit PRD generator:

1. **SYSTEM_PROMPT**: Role definition + quality rules (keep current, enhance with anti-patterns from sources)
2. **CLARIFY_PROMPT**: Keep and enhance (unique advantage over sources)
3. **OUTLINE_PROMPT** (NEW): Generate structured outline first, based on Agentic PRD's pattern
4. **DRAFT_PROMPT** (split from GENERATE_PROMPT): Expand outline into full PRD
5. **CRITIQUE_PROMPT** (NEW): Multi-perspective review (adapt AI-Native PM OS's 3-role critique)
6. **REVISE_PROMPT** (NEW): Incorporate critique, with auto-approve mechanism from Agentic PRD
7. **VALIDATE_PROMPT** (NEW): Quality scoring adapted from PRD-Taskmaster's 13-dimension grading
