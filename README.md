# PRD Copilot

> 把一句话灵感变成能过质量门禁的完整 PRD —— 一个 Claude Code skill，零服务、零依赖、零 API key。
> *A Claude Code skill that turns one-line ideas into full PRDs gated by quality checks. Prompts are in Chinese; output follows your input language.*

它不是又一个 PRD prompt。差异在三件事：

- **三道质量门**：红线扫描（8 条空洞表述 + 扩展表，字面可 grep）→ 14 项结构自检 → **独立评审**（评审跑在隔离的子代理里，只看产出不看过程——生成者不许给自己打分）。放行条件是 **P0 扣分项清零**，不是分数好看。
- **分模块生成**：4000-6000 字不截断（单次长输出必截断，是被上一版验证过的坑）。
- **澄清有纪律**：一轮 ≤4 问、素材越厚问越少、信息全清晰则 0 问、每题告诉你为什么问。

## 安装（30 秒）

```bash
git clone https://github.com/vanbuster/prd-copilot.git
mkdir -p ~/.claude/skills && ln -s "$PWD/prd-copilot/skill" ~/.claude/skills/prd-copilot
```

新开一个 Claude Code 会话，说（产出会落在当前目录 `prds/` 下）：

```
把这个想法写成 PRD：<你的一句话>
```

### 其他 Agent 运行时

skill 是纯 markdown（SKILL.md + references/），任何按 `SKILL.md` 协议热加载技能的
agent 运行时都能用——不止 Claude Code：

```bash
# 通用技能池（DSH / QClaw 等读 ~/.agents/skills/ 的运行时）
ln -s "$PWD/prd-copilot/skill" ~/.agents/skills/prd-copilot
```

symlink 保持单一真相源（`git pull` 即升级）；运行时不跟随 symlink 就改用 `cp -r`
（代价是升级要重拷）。如果池里有 dispatch 索引（如 `SKILL_INDEX.md`），注册时注意
与其他 PRD 类 skill 消歧：**产品级 0→1 完整 PRD 归本 skill，单功能详细规格归微交互
类 skill**。卸载 = 删链接（注册过 dispatch 索引的，同步移除对应条目）。

不提供网页版/独立 App：上一版就是 Web 应用（见 legacy/），全部真实价值在提示词层，
壳只会稀释它——这是被验证过的结论，不是省事。

## 三种输入方式

| 方式 | 说法 |
|---|---|
| 一句话灵感 | "把这个想法写成 PRD：……" |
| 灵感收件箱 | 平时往一个 `inbox.md` 里追加碎片想法（`- [日期] 内容`），攒够了说"从 inbox 出一份 X 的 PRD" |
| 现成文档 | 丢文件："把这份需求笔记整理成 PRD" |

## 管线

```
输入 → 吸收上下文(inbox+文档) → 澄清(≤4问,可0问) → Brief → 分模块生成(11+1)
     → 门1 红线扫描 → 门2 结构自检(14项) → 门3 独立评审(P0清零放行) → 落盘
```

产出的每份 PRD 自带：文首质量徽章、文末完整门禁报告、以及一张**「交付前需你人工确认的 N 处」清单**——AI 自动修复的和必须由你接管的分开列。你拿它去评审时，知道哪几处是 AI 的假设。

11+1 模块：产品概述 / 目标用户 / 用户故事 / 功能需求 / 非功能需求 / 信息架构 / 评估指标 / 不做什么 / 假设与约束 / 风险评估 / 里程碑，AI 产品追加 AI 专项（能力边界 / Prompt 策略 / 幻觉率指标 / 降级 / 数据飞轮 / 人机协作）。AI 产品的判定是语义级的——"智能排班系统（规则引擎）"不会被误判成 AI 产品。

## 它敢测自己

`evals/` 是本仓库的回归评测集：判定全部二值断言（约六成由 `check_structural.sh` 机判），评审强制引用原文为证据，失败的 run 不删除、不策展。初始 3 个用例：主流程冒烟 / AI 误判回归（真实历史 bug）/ 红线诱饵对抗（输入塞满空洞表述，看门禁是拦住还是复读）。用例从真实失败中生长，不预制完备覆盖。

`examples/` 里有一份**自举 PRD**——用这个 skill 给 prd-copilot 自己生成的 PRD，评审分数、扣分项、人工接管清单全部原样保留。工具敢不敢对自己用自己的门禁，是判断这类工具的最快方法。

## 定制

prompt 即代码，改 markdown 就是定制——不需要配置系统：

| 想改什么 | 改哪里 |
|---|---|
| 红线词表 / 放行标准 | `skill/references/quality-gates.md` |
| 模块结构 / 字数 / 排版 | `skill/references/modules-spec.md` |
| 行业模板 | `skill/references/industry-templates.md` |
| 澄清额度与出题法 | `skill/references/clarify-method.md` |

改完质量门相关内容，建议跑一遍 `evals/`（方法见其 README）。

## 与 Streamlit v1 的关系

本仓库的前身是一个约 2000 行的 Streamlit 应用（7+1 → 11+1 模块，含竞品搜索、双语界面、多提供商 BYOK）。它功能完整，但审计发现表现层的问题多到不值得修，而全部真实价值集中在提示词层——于是杀掉应用，把提示词资产重构为这个 skill。完整代码保留在 [`legacy/streamlit-v1/`](legacy/streamlit-v1/)，可用 `git checkout v1.0.0` 取纯净终版。这段"从应用退成管线"的历史是本仓库的一部分。

## License

MIT
