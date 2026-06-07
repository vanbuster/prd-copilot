import streamlit as st

from i18n import STEPS_ZH, STEPS_EN, STEP_ORDER
from utils.providers import get_provider


def render_toolbar(t, has_api_key):
    """Render the top toolbar (status pill + language toggle)."""
    tool_col1, tool_col2 = st.columns([8, 1])
    with tool_col2:
        if st.button("🌐 " + t("lang_label"), key="_lang_toggle"):
            st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
            st.rerun()
    with tool_col1:
        if has_api_key():
            p = get_provider()
            provider_label = p["label"]
            model_name = p["model_labels"].get(st.session_state.get("model_fast", ""), "")
            st.markdown(
                f'<div class="toolbar">'
                f'<span class="toolbar-pill active"><span class="dot"></span> {provider_label} · {model_name}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="toolbar">'
                '<span class="toolbar-pill">⚠ 未配置 API</span>'
                '</div>',
                unsafe_allow_html=True,
            )


def render_hero(t):
    """Render the hero banner."""
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


def render_progress(step, lang):
    """Render the pill-style step progress bar."""
    current_idx = STEP_ORDER.get(step, 0)
    steps = STEPS_ZH if lang == "zh" else STEPS_EN
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


def render_api_banner(t):
    """Render the 'no API key' glass card banner."""
    st.markdown(
        f'<div class="glass-card" style="text-align:center;padding:28px;">'
        f'<p style="font-size:1.05rem;color:var(--navy);margin:0 0 6px;">{t("settings_banner")}</p>'
        f'<p style="font-size:0.82rem;color:var(--muted);margin:0;">{t("setup_privacy")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_quality_score(t, score_data):
    """Render the PRD quality score card with three dimension rings."""
    sd = score_data
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"### 📊 {t('score_title')}")

    cols = st.columns(3)
    dims = [
        (t("score_completeness"), sd.get("completeness", {}).get("score", 0)),
        (t("score_quantification"), sd.get("quantification", {}).get("score", 0)),
        (t("score_executability"), sd.get("executability", {}).get("score", 0)),
    ]
    for col, (label, score) in zip(cols, dims):
        with col:
            color = "#00A67E" if score >= 75 else "#F59E0B" if score >= 50 else "#EF4444"
            bg = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)"
            st.markdown(
                f'<div style="text-align:center;">'
                f'<div class="score-ring" style="background:{bg};color:{color};border:2px solid {color}30;">{score}</div>'
                f'<div style="font-size:0.82rem;color:#6B7280;">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if sd.get("improvements"):
        st.markdown(f"**⚠ {t('score_improvement')}**")
        for imp in sd["improvements"][:3]:
            st.markdown(f"- {imp}")
    if sd.get("highlights"):
        st.markdown(f"**✓ {t('score_highlight')}**")
        for hl in sd["highlights"][:3]:
            st.markdown(f"- {hl}")
    st.markdown('</div>', unsafe_allow_html=True)
