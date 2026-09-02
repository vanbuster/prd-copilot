# Streamlit v1（已归档）

**是什么**：PRD Copilot 的初代形态——Streamlit Web 应用（澄清问卷 → 流式生成 → 质量评分 → 精修 → 导出），约 2000 行。

**怎么跑**：`pip install -r requirements.txt && cp .env.example .env`（填 DeepSeek/OpenAI 兼容 key）`&& streamlit run app.py`。纯净终版在 tag `v1.0.0`。

**为什么停**：审计发现表现层缺陷密集（状态机重复调用 LLM、token 上限截断、评分即闪即逝、零错误处理），而真实价值全部在提示词层——修壳不如迁资产。提示词的去向见仓库根 `skill/`。
