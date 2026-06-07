from prompts.refine import REFINE_PROMPT
from prompts.system import SYSTEM_PROMPT
from utils.llm import chat, get_model_pro


def refine_section(prd_content, section_name, instruction):
    """Refine a single PRD section. Returns the refined text."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": REFINE_PROMPT.format(
            current_prd=prd_content,
            section_name=section_name,
            user_instruction=instruction,
        )},
    ]
    return chat(messages, temperature=0.5, model=get_model_pro())
