import os

import streamlit as st

from components.layout import render_toolbar, render_hero, render_progress, render_api_banner, render_quality_score
from components.sidebar import render_sidebar
from i18n import I18N
from services.clarify import parse_questions
from services.generate import run_competitive_analysis, build_generation_prompt, evaluate_quality, parse_sections
from services.refine import refine_section
from templates.prd_template import detect_ai_product, get_template_options, get_template_by_index
from utils.export import export_prd, export_prd_docx
from utils.llm import chat, chat_stream, get_model_fast, get_model_pro

st.set_page_config(
    page_title="PRD Copilot",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS (cached to avoid disk read on every rerun) ──
@st.cache_data
def _load_css():
    with open("static/style.css") as f:
        return f.read()

st.markdown(f"<style>{_load_css()}</style>", unsafe_allow_html=True)


# ── State ──
def _has_api_key():
    if st.session_state.get("api_key"):
        return True
    if os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"):
        return True
    try:
        return bool(st.secrets.get("DEEPSEEK_API_KEY") or st.secrets.get("OPENAI_API_KEY"))
    except Exception:
        return False


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
        "template_idx": 0,
        "enable_search": True,
        "competitor_analysis": "",
        "quality_score": None,
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


# ── Layout ──
render_sidebar(t, _has_api_key)
render_toolbar(t, _has_api_key)
render_hero(t)
render_progress(st.session_state.step, st.session_state.lang)

if not _has_api_key():
    render_api_banner(t)
    st.stop()


# ══════════════════════════════════════════════════════════════
# Step 1: Input
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
# Step 2: Clarify
# ══════════════════════════════════════════════════════════════
elif st.session_state.step == "clarify":
    render_messages()

    with st.chat_message("assistant"):
        with st.spinner(t("analyzing")):
            from prompts.clarify import CLARIFY_PROMPT
            from prompts.system import SYSTEM_PROMPT
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": CLARIFY_PROMPT.format(
                    user_input=st.session_state.user_input
                )},
            ]
            raw = chat(messages, temperature=0.3, model=get_model_fast())

        parsed_questions = parse_questions(raw)
        st.session_state.clarify_questions = parsed_questions

        badges = '<span class="tag">AI 产品</span>' if st.session_state.is_ai_product else ""
        st.markdown(t("clarify_intro").format(badges=badges), unsafe_allow_html=True)

    final_answers = {}
    with st.form("clarify_form"):
        st.markdown(f"**{t('template_label')}**")
        template_options = get_template_options(st.session_state.lang)
        selected_template = st.selectbox(
            t("template_label"),
            options=template_options,
            index=st.session_state.template_idx,
            label_visibility="collapsed",
        )
        st.session_state.template_idx = template_options.index(selected_template)

        enable_search = st.checkbox(t("enable_search"), value=st.session_state.enable_search)
        st.markdown("---")

        for i, q_data in enumerate(parsed_questions):
            q_text = q_data["question"]
            opts = q_data.get("options", [])
            select_type = q_data.get("select_type", "multi")

            if opts and len(opts) >= 2:
                mode_hint = t("single_hint") if select_type == "single" else t("multi_hint")
                st.markdown(f"**{i+1}. {q_text}**（{mode_hint}）")

                if select_type == "single":
                    selected = st.radio("选择一个", options=opts, key=f"q_{i}", label_visibility="collapsed")
                    selected_items = [selected]
                else:
                    selected_items = []
                    for j, opt in enumerate(opts):
                        if st.checkbox(opt, key=f"cb_{i}_{j}"):
                            selected_items.append(opt)

                custom = st.text_input(f"q_custom_{i}", placeholder=t("custom_placeholder"), label_visibility="collapsed")
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
            st.session_state.enable_search = enable_search
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
# Step 3: Generate PRD
# ══════════════════════════════════════════════════════════════
elif st.session_state.step == "generate":
    render_messages()

    with st.chat_message("assistant"):
        template = get_template_by_index(st.session_state.template_idx)

        competitor_section = ""
        search_used = False
        if st.session_state.enable_search:
            with st.spinner(t("competitor_searching")):
                competitor_section, search_used = run_competitive_analysis(
                    st.session_state.user_input
                )
            st.session_state.competitor_analysis = competitor_section
            label = f"🔍 {t('competitor_found')}"
            if not search_used:
                label += t("competitor_fallback")
            with st.expander(label, expanded=False):
                st.markdown(competitor_section)

        messages = build_generation_prompt(
            st.session_state.user_input,
            st.session_state.clarify_answers,
            st.session_state.is_ai_product,
            template,
            competitor_section,
        )
        with st.spinner(t("generating")):
            prd_placeholder = st.empty()
            prd_text = ""
            for chunk in chat_stream(messages, temperature=0.5, max_tokens=4096, model=get_model_pro()):
                prd_text += chunk
                prd_placeholder.markdown(prd_text)

        st.session_state.prd_content = prd_text

        with st.spinner(t("evaluating")):
            st.session_state.quality_score = evaluate_quality(prd_text)
        if st.session_state.quality_score:
            render_quality_score(t, st.session_state.quality_score)

        st.session_state.prd_sections = parse_sections(prd_text, competitor_section)
        add_message("assistant", prd_text)
        st.session_state.step = "refine"
        st.rerun()


# ══════════════════════════════════════════════════════════════
# Step 4: Refine
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
        selected = st.radio(t("refine_nav"), options=section_titles, label_visibility="collapsed")

        refine_instruction = st.text_area(
            t("refine_nav"),
            placeholder=t("refine_placeholder"),
            height=80,
            label_visibility="collapsed",
        )

        if st.button(t("refine_btn"), use_container_width=True):
            with st.spinner(t("refining_spinner")):
                refined = refine_section(
                    st.session_state.prd_content,
                    selected,
                    refine_instruction or t("refine_default"),
                )
            old = st.session_state.prd_sections.get(selected, "")
            st.session_state.prd_sections[selected] = refined
            st.session_state.prd_content = st.session_state.prd_content.replace(old, refined)
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
# Step 5: Export
# ══════════════════════════════════════════════════════════════
elif st.session_state.step == "export":
    st.markdown(f"### {t('preview_title')}")
    st.markdown(st.session_state.prd_content)

    filename, full_content = export_prd(st.session_state.prd_content, st.session_state.user_input)
    word_filename, word_bytes = export_prd_docx(st.session_state.prd_content, st.session_state.user_input)

    dl1, dl2, dl3 = st.columns(3)
    with dl1:
        st.download_button(
            t("download_btn"), data=full_content, file_name=filename,
            mime="text/markdown", use_container_width=True, type="primary",
        )
    with dl2:
        st.download_button(
            t("download_word_btn"), data=word_bytes, file_name=word_filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True, type="primary",
        )
    with dl3:
        if st.button(t("copy_clipboard_btn"), use_container_width=True):
            st.session_state.copied = True
            st.rerun()

    if st.session_state.get("copied"):
        st.success(t("copied"))
        st.code(full_content, language="markdown")

    st.markdown("---")
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button(t("back_refine_btn"), use_container_width=True):
            st.session_state.pop("copied", None)
            st.session_state.step = "refine"
            st.rerun()
    with nav2:
        if st.button(t("restart_btn"), use_container_width=True):
            reset()
            st.rerun()
