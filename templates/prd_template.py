PRD_SECTIONS = [
    {
        "key": "overview",
        "title": "产品概述",
        "title_en": "Product Overview",
    },
    {
        "key": "users",
        "title": "目标用户",
        "title_en": "Target Users",
    },
    {
        "key": "stories",
        "title": "用户故事",
        "title_en": "User Stories",
    },
    {
        "key": "requirements",
        "title": "功能需求",
        "title_en": "Functional Requirements",
    },
    {
        "key": "non_functional",
        "title": "非功能需求",
        "title_en": "Non-Functional Requirements",
    },
    {
        "key": "architecture",
        "title": "信息架构",
        "title_en": "Information Architecture",
    },
    {
        "key": "metrics",
        "title": "评估指标",
        "title_en": "Success Metrics",
    },
    {
        "key": "ai",
        "title": "AI 专项",
        "title_en": "AI Considerations",
        "optional": True,
    },
]


def get_section_titles():
    return [s["title"] for s in PRD_SECTIONS if not s.get("optional")]


def get_all_section_titles():
    return [s["title"] for s in PRD_SECTIONS]


def get_section_key_by_title(title):
    for s in PRD_SECTIONS:
        if s["title"] == title:
            return s["key"]
    return None


AI_KEYWORDS = [
    "AI", "ai", "人工智能", "智能", "模型", "大模型", "大语言模型", "LLM",
    "推荐", "生成", "识别", "预测", "分类", "Agent", "agent", "智能体",
    "Chatbot", "chatbot", "聊天机器人", "对话", "NLP", "自然语言",
    "CV", "计算机视觉", "语音", "GPT", "ChatGPT", "DeepSeek", "Claude",
    "机器学习", "深度学习", "训练", "微调", "fine-tune",
]


def detect_ai_product(text):
    return any(kw in text for kw in AI_KEYWORDS)
