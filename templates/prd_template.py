PRD_TEMPLATES = [
    {
        "key": "general",
        "title": "通用产品",
        "title_en": "General Product",
        "icon": "📋",
        "focus": "",
    },
    {
        "key": "saas",
        "title": "SaaS 产品",
        "title_en": "SaaS Product",
        "icon": "☁️",
        "focus": "定价策略、订阅模式、租户隔离、数据权限、API 开放、计费逻辑",
    },
    {
        "key": "mobile",
        "title": "移动端 App",
        "title_en": "Mobile App",
        "icon": "📱",
        "focus": "推送策略、离线模式、手势交互、性能优化（启动速度、包体积）、应用商店优化",
    },
    {
        "key": "ai",
        "title": "AI 应用",
        "title_en": "AI Application",
        "icon": "🤖",
        "focus": "模型能力边界、Prompt 策略、准确率/幻觉率、降级兜底、数据飞轮、人机协作模式",
    },
    {
        "key": "ecommerce",
        "title": "电商产品",
        "title_en": "E-commerce",
        "icon": "🛒",
        "focus": "商品信息架构、搜索推荐、购物车/结算、库存、物流跟踪、售后",
    },
    {
        "key": "b2b",
        "title": "B2B 平台",
        "title_en": "B2B Platform",
        "icon": "🏢",
        "focus": "组织架构与权限、审批流、数据看板、多角色工作台、集成能力",
    },
]


def get_template_options(lang="zh"):
    return [
        f"{t['icon']} {t['title'] if lang == 'zh' else t['title_en']}"
        for t in PRD_TEMPLATES
    ]


def get_template_by_index(idx):
    if 0 <= idx < len(PRD_TEMPLATES):
        return PRD_TEMPLATES[idx]
    return PRD_TEMPLATES[0]


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
