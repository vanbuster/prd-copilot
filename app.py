import json
import re

import streamlit as st

from prompts.clarify import CLARIFY_PROMPT
from prompts.generate import GENERATE_PROMPT
from prompts.refine import REFINE_PROMPT
from prompts.system import SYSTEM_PROMPT
from templates.prd_template import detect_ai_product
from utils.export import export_prd
from utils.llm import chat, MODEL_FAST, MODEL_PRO

st.set_page_config(
    page_title="PRD Copilot",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 注入 CSS ──
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ── i18n ──
I18N = {
    "zh": {
        "subtitle": "一句话描述你的产品想法，AI 帮你生成结构化 PRD 大纲",
        "tip_prefix": "💡 提示：",
        "tips": [
            "试试描述一个你想做的产品，比如：一个帮助大学生规划职业路径的AI助手",
            "你可以用一句话开始，也可以详细描述——我会帮你补全缺失的信息",
            "越具体的描述，生成的 PRD 质量越高哦",
        ],
        "input_placeholder": "描述你想做的产品或功能，越详细越好...",
        "input_too_short": "请多描述一些细节，至少 10 个字",
        "analyzing": "正在分析你的需求...",
        "clarify_intro": "我已经理解了你的想法 {badges}。<br/>为了生成更精准的 PRD，请回答以下问题：",
        "multi_hint": "可多选",
        "single_hint": "单选",
        "custom_placeholder": "补充其他想法（可选）...",
        "generate_btn": "生成 PRD →",
        "answer_required": "请至少回答一个问题",
        "generating": "正在生成 PRD 大纲，请稍候...",
        "refining_spinner": "正在精修...",
        "refine_title": "精修 PRD",
        "refine_caption": "选择模块展开补充，或直接导出",
        "refine_nav": "模块导航",
        "refine_placeholder": "补充更多用户故事、细化指标...",
        "refine_btn": "精修选中模块",
        "refine_default": "展开该模块的细节，增加更多具体内容",
        "refine_done": "精修完成",
        "export_btn": "完成，导出 PRD →",
        "restart_btn": "重新开始",
        "preview_title": "PRD 预览",
        "download_btn": "📥 下载 PRD (Markdown)",
        "back_refine_btn": "返回精修",
        "lang_label": "English",
    },
    "en": {
        "subtitle": "Describe your product idea in one sentence, AI generates a structured PRD outline",
        "tip_prefix": "💡 Tip: ",
        "tips": [
            "Try describing a product you want to build, e.g.: an AI assistant for college students to plan career paths",
            "Start with one sentence or go into detail — I'll help fill in the gaps",
            "More specific descriptions lead to higher quality PRDs",
        ],
        "input_placeholder": "Describe the product or feature you want to build...",
        "input_too_short": "Please provide more details, at least 10 characters",
        "analyzing": "Analyzing your requirements...",
        "clarify_intro": "I understand your idea {badges}.<br/>To generate a more precise PRD, please answer:",
        "multi_hint": "multi-select",
        "single_hint": "single-select",
        "custom_placeholder": "Add more details (optional)...",
        "generate_btn": "Generate PRD →",
        "answer_required": "Please answer at least one question",
        "generating": "Generating PRD outline, please wait...",
        "refining_spinner": "Refining...",
        "refine_title": "Refine PRD",
        "refine_caption": "Select a section to expand, or export directly",
        "refine_nav": "Section Navigator",
        "refine_placeholder": "Add more user stories, refine metrics...",
        "refine_btn": "Refine Selected Section",
        "refine_default": "Expand this section with more details",
        "refine_done": "Refinement complete",
        "export_btn": "Done, Export PRD →",
        "restart_btn": "Start Over",
        "preview_title": "PRD Preview",
        "download_btn": "📥 Download PRD (Markdown)",
        "back_refine_btn": "Back to Refine",
        "lang_label": "中文",
    },
}

STEPS_ZH = ["描述需求", "澄清细节", "生成 PRD", "精修内容", "导出文档"]
STEPS_EN = ["Describe", "Clarify", "Generate PRD", "Refine", "Export"]
STEP_ORDER = {k: i for i, k in enumerate(["input", "clarify", "generate", "refine", "export"])}


# ── 状态管理 ──
def init_state():
    defaults = {
        "step": "input",
        "user_input": "",
        "clarify_questions": [],
        "clarify_answers": {},
        "prd_content": "",
        "prd_sections": {},
        "is_ai_product": False,
        "messages": [],
        "lang": "zh",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


def t(key):
    return I18N[st.session_state.lang][key]


def reset():
    lang = st.session_state.get("lang", "zh")
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_state()
    st.session_state.lang = lang


def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})


def render_messages():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)


def render_progress():
    current_idx = STEP_ORDER.get(st.session_state.step, 0)
    steps = STEPS_ZH if st.session_state.lang == "zh" else STEPS_EN
    html_parts = ['<div class="progress-bar">']
    for i, label in enumerate(steps):
        if i > 0:
            conn_class = "done" if i <= current_idx else ""
            html_parts.append(f'<div class="step-connector {conn_class}"></div>')
        if i < current_idx:
            html_parts.append(f'<div class="step-node done">✓ {label}</div>')
        elif i == current_idx:
            html_parts.append(f'<div class="step-node active">● {label}</div>')
        else:
            html_parts.append(f'<div class="step-node">{label}</div>')
    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


# ── 语言切换 ──
col_spacer, col_lang = st.columns([8, 1])
with col_lang:
    st.markdown('<div class="lang-toggle">', unsafe_allow_html=True)
    if st.button("🌐 " + t("lang_label")):
        st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Hero ──
st.markdown(
    """
    <div class="hero-banner" style="text-align:center;">
        <p class="greeting">Hey, Captain，我是你的 PRD Copilot</p>
        <h1>今天想做点什么改变世界的事？</h1>
        <p class="subtitle">""" + t("subtitle") + """</p>
    </div>
    """,
    unsafe_allow_html=True,
)

render_progress()


# ══════════════════════════════════════════════════════════════
# Step 1: 用户输入
# ══════════════════════════════════════════════════════════════
if st.session_state.step == "input":
    if not st.session_state.messages:
        import random
        st.markdown(
            f'<div class="ai-card ai-card--highlight">'
            f'<p style="color:#6B7280;margin:0;">{t("tip_prefix")}{random.choice(t("tips"))}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    render_messages()
    if prompt := st.chat_input(t("input_placeholder")):
        if len(prompt.strip()) < 10:
            st.warning(t("input_too_short"))
            st.stop()

        st.session_state.user_input = prompt.strip()
        st.session_state.is_ai_product = detect_ai_product(prompt)
        add_message("user", prompt)
        st.session_state.step = "clarify"
        st.rerun()


# ══════════════════════════════════════════════════════════════
# Step 2: 澄清问题（多选 + 单选，flash 模型）
# ══════════════════════════════════════════════════════════════
elif st.session_state.step == "clarify":
    render_messages()

    with st.chat_message("assistant"):
        with st.spinner(t("analyzing")):
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": CLARIFY_PROMPT.format(
                    user_input=st.session_state.user_input
                )},
            ]
            raw = chat(messages, temperature=0.3, model=MODEL_FAST)

        parsed_questions = []
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict) and "question" in item:
                        parsed_questions.append({
                            "question": item["question"],
                            "options": item.get("options", []),
                            "select_type": item.get("select_type", "multi"),
                        })
                    elif isinstance(item, str):
                        parsed_questions.append({
                            "question": item,
                            "options": [],
                            "select_type": "multi",
                        })
        except json.JSONDecodeError:
            lines = [l.strip("- ").strip() for l in raw.strip().split("\n") if l.strip()]
            for l in lines[:5]:
                parsed_questions.append({"question": l, "options": [], "select_type": "multi"})

        parsed_questions = parsed_questions[:5]
        st.session_state.clarify_questions = parsed_questions

        badges = ""
        if st.session_state.is_ai_product:
            badges = '<span class="tag">AI 产品</span>'

        st.markdown(
            t("clarify_intro").format(badges=badges),
            unsafe_allow_html=True,
        )

    final_answers = {}
    with st.form("clarify_form"):
        for i, q_data in enumerate(parsed_questions):
            q_text = q_data["question"]
            opts = q_data.get("options", [])
            select_type = q_data.get("select_type", "multi")

            if opts and len(opts) >= 2:
                mode_hint = t("single_hint") if select_type == "single" else t("multi_hint")
                st.markdown(f"**{i+1}. {q_text}**（{mode_hint}）")

                if select_type == "single":
                    selected = st.radio(
                        "选择一个",
                        options=opts,
                        key=f"q_{i}",
                        label_visibility="collapsed",
                    )
                    selected_items = [selected]
                else:
                    selected_items = []
                    for j, opt in enumerate(opts):
                        if st.checkbox(opt, key=f"cb_{i}_{j}"):
                            selected_items.append(opt)

                custom = st.text_input(
                    f"q_custom_{i}",
                    placeholder=t("custom_placeholder"),
                    label_visibility="collapsed",
                )

                parts = list(selected_items) if selected_items else []
                if custom:
                    parts.append(custom)
                final_answers[i] = "；".join(parts) if parts else ""

                if i < len(parsed_questions) - 1:
                    st.markdown("<hr/>", unsafe_allow_html=True)
            else:
                final_answers[i] = st.text_input(q_text, key=f"q_{i}")

        submitted = st.form_submit_button(t("generate_btn"), use_container_width=True)

        if submitted:
            st.session_state.clarify_answers = {
                parsed_questions[i]["question"]: final_answers[i]
                for i in range(len(parsed_questions)) if final_answers.get(i)
            }
            if not st.session_state.clarify_answers:
                st.warning(t("answer_required"))
                st.stop()
            qa_summary = "\n".join(
                f"**Q: {q}**\nA: {a}" for q, a in st.session_state.clarify_answers.items()
            )
            add_message("assistant", f"**澄清问答：**\n\n{qa_summary}")
            st.session_state.step = "generate"
            st.rerun()


# ══════════════════════════════════════════════════════════════
# Step 3: 生成 PRD（pro 模型）
# ══════════════════════════════════════════════════════════════
elif st.session_state.step == "generate":
    render_messages()

    with st.chat_message("assistant"):
        with st.spinner(t("generating")):
            clarify_qa = "\n".join(
                f"Q: {q}\nA: {a}" for q, a in st.session_state.clarify_answers.items()
            )
            ai_section = ""
            if st.session_state.is_ai_product:
                ai_section = (
                    "### 8. AI 专项\n"
                    "- 模型能力边界（能做什么/不能做什么）\n"
                    "- Prompt 设计策略\n"
                    "- 准确率/幻觉率指标要求\n"
                    "- 降级策略（模型不可用时的兜底方案）"
                )

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": GENERATE_PROMPT.format(
                    user_input=st.session_state.user_input,
                    clarify_qa=clarify_qa,
                    is_ai_product="是" if st.session_state.is_ai_product else "否",
                    ai_section=ai_section,
                )},
            ]
            prd = chat(messages, temperature=0.5, max_tokens=4096, model=MODEL_PRO)

        st.session_state.prd_content = prd
        st.markdown(prd)

        # 解析各模块
        sections = {}
        pattern = r"^##\s+(\d+\.\s+.+)$"
        lines = prd.split("\n")
        current_section = None
        current_lines = []

        for line in lines:
            match = re.match(pattern, line)
            if match:
                if current_section:
                    sections[current_section] = "\n".join(current_lines)
                current_section = match.group(1)
                current_lines = [line]
            elif current_section:
                current_lines.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_lines)

        st.session_state.prd_sections = sections
        add_message("assistant", prd)
        st.session_state.step = "refine"
        st.rerun()


# ══════════════════════════════════════════════════════════════
# Step 4: 逐节精修（pro 模型）
# ══════════════════════════════════════════════════════════════
elif st.session_state.step == "refine":
    render_messages()

    st.markdown(f"### {t('refine_title')}")
    st.caption(t("refine_caption"))

    section_titles = list(st.session_state.prd_sections.keys())
    col_nav, col_content = st.columns([1, 2.5])

    with col_nav:
        st.markdown('<div class="refine-nav">', unsafe_allow_html=True)
        st.markdown(f"**{t('refine_nav')}**")
        selected = st.radio(
            t("refine_nav"),
            options=section_titles,
            label_visibility="collapsed",
        )

        refine_instruction = st.text_area(
            t("refine_nav"),
            placeholder=t("refine_placeholder"),
            height=80,
            label_visibility="collapsed",
        )

        if st.button(t("refine_btn"), use_container_width=True):
            with st.spinner(t("refining_spinner")):
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": REFINE_PROMPT.format(
                        current_prd=st.session_state.prd_content,
                        section_name=selected,
                        user_instruction=refine_instruction or t("refine_default"),
                    )},
                ]
                refined = chat(messages, temperature=0.5, model=MODEL_PRO)

            old = st.session_state.prd_sections.get(selected, "")
            st.session_state.prd_sections[selected] = refined
            st.session_state.prd_content = st.session_state.prd_content.replace(
                old, refined
            )
            st.success(t("refine_done"))
            st.rerun()

        st.markdown("---")
        if st.button(t("export_btn"), use_container_width=True, type="primary"):
            st.session_state.step = "export"
            st.rerun()

        if st.button(t("restart_btn"), use_container_width=True):
            reset()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_content:
        if selected and selected in st.session_state.prd_sections:
            st.markdown(st.session_state.prd_sections[selected])


# ══════════════════════════════════════════════════════════════
# Step 5: 导出 PRD
# ══════════════════════════════════════════════════════════════
elif st.session_state.step == "export":
    st.markdown(f"### {t('preview_title')}")
    st.markdown(st.session_state.prd_content)

    filename, full_content = export_prd(
        st.session_state.prd_content, st.session_state.user_input
    )

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.download_button(
            t("download_btn"),
            data=full_content,
            file_name=filename,
            mime="text/markdown",
            use_container_width=True,
            type="primary",
        )
    with col2:
        if st.button(t("back_refine_btn"), use_container_width=True):
            st.session_state.step = "refine"
            st.rerun()
    with col3:
        if st.button(t("restart_btn"), use_container_width=True):
            reset()
            st.rerun()
