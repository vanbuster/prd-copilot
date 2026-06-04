from datetime import datetime


def export_prd(prd_content, user_input=""):
    first_line = user_input.strip().split("\n")[0][:30] if user_input else "product"
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"PRD_{first_line}_{date_str}.md"

    header = f"""# 产品需求文档 (PRD)

> 由 PRD Copilot 自动生成
> 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}

---

"""
    full_content = header + prd_content
    return filename, full_content
