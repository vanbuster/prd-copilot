import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None

MODEL_FAST = os.getenv("MODEL_FAST", "deepseek-v4-flash")
MODEL_PRO = os.getenv("MODEL_PRO", "deepseek-v4-pro")


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
        if not api_key:
            raise ValueError(
                "请设置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY 环境变量。\n"
                "复制 .env.example 为 .env 并填入你的 API Key。"
            )
        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client


def chat(messages, temperature=0.7, max_tokens=4096, model=None):
    use_model = model or MODEL_FAST
    client = get_client()
    response = client.chat.completions.create(
        model=use_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
