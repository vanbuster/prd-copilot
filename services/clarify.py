import json


def parse_questions(raw_text):
    """Parse clarification questions from LLM response."""
    questions = []
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict) and "question" in item:
                    questions.append({
                        "question": item["question"],
                        "options": item.get("options", []),
                        "select_type": item.get("select_type", "multi"),
                    })
                elif isinstance(item, str):
                    questions.append({
                        "question": item,
                        "options": [],
                        "select_type": "multi",
                    })
    except json.JSONDecodeError:
        lines = [l.strip("- ").strip() for l in raw_text.strip().split("\n") if l.strip()]
        for l in lines[:5]:
            questions.append({"question": l, "options": [], "select_type": "multi"})

    return questions[:5]
