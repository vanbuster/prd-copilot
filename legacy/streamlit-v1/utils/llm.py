import hashlib
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None
_client_signature = None

MODEL_FAST = os.getenv("MODEL_FAST", "deepseek-chat")
MODEL_PRO = os.getenv("MODEL_PRO", "deepseek-chat")


def _resolve_config():
    """Resolve API config: session_state > env > st.secrets."""
    api_key = None
    base_url = None
    model_fast = MODEL_FAST
    model_pro = MODEL_PRO

    try:
        import streamlit as st
        if st.session_state.get("api_key"):
            api_key = st.session_state.api_key
            base_url = st.session_state.get("base_url")
            model_fast = st.session_state.get("model_fast", model_fast)
            model_pro = st.session_state.get("model_pro", model_pro)
    except Exception:
        pass

    if not api_key:
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")

    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("DEEPSEEK_API_KEY") or st.secrets.get("OPENAI_API_KEY")
            base_url = base_url or st.secrets.get("OPENAI_BASE_URL", base_url or "https://api.deepseek.com")
        except Exception:
            pass

    if not base_url:
        base_url = "https://api.deepseek.com"

    return api_key, base_url, model_fast, model_pro


def get_client():
    global _client, _client_signature
    api_key, base_url, model_fast, model_pro = _resolve_config()

    if not api_key:
        raise ValueError(
            "请设置 API Key。\n"
            "方式一：在页面设置面板中填写\n"
            "方式二：在 .env 文件中填写"
        )

    sig = (hashlib.sha256(api_key.encode()).hexdigest()[:16], base_url)
    if _client is None or _client_signature != sig:
        _client = OpenAI(api_key=api_key, base_url=base_url)
        _client_signature = sig
    return _client


def reset_client():
    global _client, _client_signature
    _client = None
    _client_signature = None


def get_model_fast():
    _, _, model_fast, _ = _resolve_config()
    return model_fast


def get_model_pro():
    _, _, _, model_pro = _resolve_config()
    return model_pro


def chat(messages, temperature=0.7, max_tokens=4096, model=None):
    _, _, model_fast, _ = _resolve_config()
    use_model = model or model_fast
    client = get_client()
    response = client.chat.completions.create(
        model=use_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def chat_stream(messages, temperature=0.7, max_tokens=4096, model=None):
    _, _, model_fast, _ = _resolve_config()
    use_model = model or model_fast
    client = get_client()
    stream = client.chat.completions.create(
        model=use_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
