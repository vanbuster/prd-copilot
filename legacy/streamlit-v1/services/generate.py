import json
import re

from prompts.competitive import COMPETITIVE_PROMPT
from prompts.evaluate import EVALUATE_PROMPT
from prompts.generate import GENERATE_PROMPT
from prompts.system import SYSTEM_PROMPT
from utils.llm import chat, get_client, get_model_fast
from utils.search import execute_search, SEARCH_TOOL


def run_competitive_analysis(user_input):
    """Agent-style competitive analysis with tool calling.
    Returns (competitor_section, search_used).
    """
    client = get_client()
    agent_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"分析以下产品的竞争格局，生成竞品分析报告：\n\n"
            f"{user_input}\n\n"
            f"如果有可用的搜索工具，优先搜索获取最新竞品信息；"
            f"如果搜索不可用，基于你的知识进行分析。"
            f"输出格式：竞品概览表格 + 差异化机会 + 市场空白。"
        )},
    ]

    search_used = False
    competitor_section = ""

    for _ in range(2):
        response = client.chat.completions.create(
            model=get_model_fast(),
            messages=agent_messages,
            tools=[SEARCH_TOOL],
            temperature=0.3,
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            agent_messages.append(msg)
            for tc in msg.tool_calls:
                if tc.function.name == "web_search":
                    args = json.loads(tc.function.arguments)
                    search_result = execute_search(args.get("query", user_input))
                    search_used = "error" not in search_result
                    agent_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": search_result,
                    })
        else:
            competitor_section = msg.content or ""
            break

    if not competitor_section:
        competitor_section = chat(
            [{"role": "system", "content": SYSTEM_PROMPT},
             {"role": "user", "content": COMPETITIVE_PROMPT.format(
                 user_input=user_input,
             )}],
            temperature=0.3, model=get_model_fast(),
        )

    return competitor_section, search_used


def build_generation_prompt(user_input, clarify_answers, is_ai_product, template, competitor_section):
    """Assemble the full PRD generation prompt. Returns message list."""
    clarify_qa = "\n".join(
        f"Q: {q}\nA: {a}" for q, a in clarify_answers.items()
    )

    ai_section = ""
    if is_ai_product:
        ai_section = (
            "\n## 12. AI 专项\n"
            "- 模型能力边界（能做什么/不能做什么）\n"
            "- Prompt 设计策略\n"
            "- 准确率/幻觉率指标要求\n"
            "- 降级策略（模型不可用时的兜底方案）"
        )

    template_focus = ""
    if template["focus"]:
        template_focus = (
            f"\n\n## 行业模板聚焦（{template['title']}）\n"
            f"请在功能需求和非功能需求中重点覆盖以下领域：{template['focus']}"
        )

    competitor_block = ""
    if competitor_section:
        competitor_block = (
            "\n\n## 竞品分析参考\n"
            "以下是基于市场搜索得到的竞品分析，请在 PRD 的差异化部分参考：\n"
            f"{competitor_section}"
        )

    full_prompt = GENERATE_PROMPT.format(
        user_input=user_input,
        clarify_qa=clarify_qa,
        is_ai_product="是" if is_ai_product else "否",
        ai_section=ai_section,
    ) + template_focus + competitor_block

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": full_prompt},
    ]


def evaluate_quality(prd_content):
    """Evaluate PRD quality. Returns score dict or None."""
    eval_messages = [
        {"role": "user", "content": EVALUATE_PROMPT.format(prd_content=prd_content)},
    ]
    eval_raw = chat(eval_messages, temperature=0.2, model=get_model_fast())
    try:
        json_match = re.search(r"\{[\s\S]+\}", eval_raw)
        if json_match:
            return json.loads(json_match.group())
    except (json.JSONDecodeError, AttributeError):
        pass
    return None


def parse_sections(prd_text, competitor_section=""):
    """Parse PRD text into sections by ## numbered headings."""
    sections = {}
    pattern = r"^##\s+(\d+\.\s+.+)$"
    lines = prd_text.split("\n")
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

    if competitor_section:
        sections["竞品分析"] = competitor_section

    return sections
