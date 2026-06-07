PROVIDERS = {
    "deepseek": {
        "label": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "env_key": "DEEPSEEK_API_KEY",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "model_labels": {
            "deepseek-chat": "DeepSeek V4 Flash",
            "deepseek-reasoner": "DeepSeek R1",
        },
        "default_fast": "deepseek-chat",
        "default_pro": "deepseek-reasoner",
        "doc_url": "https://platform.deepseek.com/api_keys",
    },
    "openai": {
        "label": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "env_key": "OPENAI_API_KEY",
        "models": ["gpt-4o-mini", "gpt-4o", "o3-mini"],
        "model_labels": {
            "gpt-4o-mini": "GPT-4o Mini",
            "gpt-4o": "GPT-4o",
            "o3-mini": "o3-mini",
        },
        "default_fast": "gpt-4o-mini",
        "default_pro": "gpt-4o",
        "doc_url": "https://platform.openai.com/api-keys",
    },
    "claude": {
        "label": "Claude (Anthropic)",
        "base_url": "https://api.anthropic.com/v1",
        "env_key": "ANTHROPIC_API_KEY",
        "models": ["claude-sonnet-4-6", "claude-opus-4-7"],
        "model_labels": {
            "claude-sonnet-4-6": "Claude Sonnet 4.6",
            "claude-opus-4-7": "Claude Opus 4.7",
        },
        "default_fast": "claude-sonnet-4-6",
        "default_pro": "claude-opus-4-7",
        "doc_url": "https://console.anthropic.com/settings/keys",
        "note": "需使用 OpenAI 兼容代理或自定义 base_url",
    },
    "zhipu": {
        "label": "智谱 GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "env_key": "ZHIPU_API_KEY",
        "models": ["glm-4-flash", "glm-4-plus", "glm-4-air"],
        "model_labels": {
            "glm-4-flash": "GLM-4 Flash",
            "glm-4-plus": "GLM-4 Plus",
            "glm-4-air": "GLM-4 Air",
        },
        "default_fast": "glm-4-flash",
        "default_pro": "glm-4-plus",
        "doc_url": "https://open.bigmodel.cn/usercenter/apikeys",
    },
    "qwen": {
        "label": "通义千问",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "env_key": "QWEN_API_KEY",
        "models": ["qwen-plus", "qwen-max", "qwen-turbo"],
        "model_labels": {
            "qwen-plus": "Qwen Plus",
            "qwen-max": "Qwen Max",
            "qwen-turbo": "Qwen Turbo",
        },
        "default_fast": "qwen-plus",
        "default_pro": "qwen-max",
        "doc_url": "https://dashscope.console.aliyun.com/apiKey",
    },
    "doubao": {
        "label": "豆包 (字节跳动)",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "env_key": "DOUBAO_API_KEY",
        "models": ["doubao-1.5-pro-32k", "doubao-1.5-pro-256k"],
        "model_labels": {
            "doubao-1.5-pro-32k": "豆包 1.5 Pro 32K",
            "doubao-1.5-pro-256k": "豆包 1.5 Pro 256K",
        },
        "default_fast": "doubao-1.5-pro-32k",
        "default_pro": "doubao-1.5-pro-256k",
        "doc_url": "https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey",
    },
    "custom": {
        "label": "自定义 (OpenAI 兼容)",
        "base_url": "",
        "env_key": "CUSTOM_API_KEY",
        "models": [],
        "model_labels": {},
        "default_fast": "",
        "default_pro": "",
        "doc_url": "",
    },
}

PROVIDER_OPTIONS = list(PROVIDERS.keys())


def get_provider(provider_key=None):
    """Resolve provider config from session_state or default to deepseek."""
    if provider_key is None:
        try:
            import streamlit as st
            provider_key = st.session_state.get("provider_key", "deepseek")
        except Exception:
            provider_key = "deepseek"
    return PROVIDERS.get(provider_key, PROVIDERS["deepseek"])
