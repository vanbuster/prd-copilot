import streamlit as st

from utils.llm import reset_client
from utils.providers import PROVIDERS, PROVIDER_OPTIONS, get_provider


def render_sidebar(t, has_api_key):
    """Render the Settings sidebar (API key + model switcher)."""
    with st.sidebar:
        st.markdown(f'<div class="sidebar-title">⚙️ {t("settings_title")}</div>', unsafe_allow_html=True)

        current_pk = st.session_state.get("provider_key", "deepseek")
        provider_idx = PROVIDER_OPTIONS.index(current_pk) if current_pk in PROVIDER_OPTIONS else 0

        provider_key = st.selectbox(
            t("setup_provider"),
            options=PROVIDER_OPTIONS,
            format_func=lambda k: PROVIDERS[k]["label"],
            index=provider_idx,
            key="_sb_provider",
        )

        api_key_input = st.text_input(
            t("setup_api_key"),
            type="password",
            placeholder=t("setup_api_key_hint"),
            key="_sb_api_key",
        )

        provider = PROVIDERS[provider_key]

        if provider_key == "custom":
            st.text_input(
                t("setup_base_url"),
                placeholder="https://api.example.com/v1",
                key="_sb_base_url",
            )

        if provider["doc_url"]:
            st.markdown(
                f"<a href='{provider['doc_url']}' target='_blank' class='sidebar-link'>{t('setup_get_key')}</a>",
                unsafe_allow_html=True,
            )

        if st.button(t("setup_start"), type="primary", use_container_width=True, key="_sb_save"):
            if not api_key_input:
                st.warning(t("setup_required"))
            else:
                is_custom = provider_key == "custom"
                st.session_state.api_key = api_key_input
                st.session_state.provider_key = provider_key
                st.session_state.base_url = "" if is_custom else provider["base_url"]
                if is_custom:
                    st.session_state.base_url = st.session_state.get("_sb_base_url", "")
                st.session_state.model_fast = provider.get("default_fast", "")
                st.session_state.model_pro = provider.get("default_pro", "")
                reset_client()
                st.toast(t("settings_saved"))
                st.rerun()

        st.markdown(f'<p class="privacy">{t("setup_privacy")}</p>', unsafe_allow_html=True)

        if has_api_key():
            st.markdown("---")
            p = get_provider()
            if p["models"]:
                current_m = st.session_state.get("model_fast", p["default_fast"])
                labels = p["model_labels"]
                available = p["models"]
                m_idx = available.index(current_m) if current_m in available else 0
                chosen = st.selectbox(
                    t("model_label"),
                    options=available,
                    format_func=lambda m: labels.get(m, m),
                    index=m_idx,
                    key="_sb_model",
                )
                if chosen != st.session_state.get("model_fast"):
                    st.session_state.model_fast = chosen
                    st.session_state.model_pro = chosen
                    reset_client()
