import json
import os
import re

import requests


SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "搜索互联网获取产品竞品信息、市场数据和行业动态。当需要了解竞品、市场格局、行业趋势时调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，如'AI 职业规划 产品竞品'",
                }
            },
            "required": ["query"],
        },
    }
}


def _get_proxies():
    proxy = (
        os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
        or os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    )
    if proxy:
        return {"http": proxy, "https": proxy}
    return None


def _search_ddg(query: str, max_results: int = 6):
    proxies = _get_proxies()
    try:
        resp = requests.post(
            "https://lite.duckduckgo.com/lite/",
            data={"q": query},
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
                ),
            },
            proxies=proxies,
            timeout=10,
        )
        resp.raise_for_status()
        links = re.findall(
            r'<a[^>]*rel="nofollow"[^>]*href="([^"]+)"[^>]*>([^<]*)</a>',
            resp.text,
        )
        if not links:
            return []
        rows = resp.text.split("<tr>")
        snippets = [re.sub(r"<[^>]+>", "", r).replace("&nbsp;", " ").strip() for r in rows]

        results = []
        for i, (url, title) in enumerate(links[:max_results]):
            snippet = ""
            for j, s in enumerate(snippets):
                if title.strip()[:30] in s:
                    for k in range(j + 1, min(j + 4, len(snippets))):
                        candidate = snippets[k]
                        if len(candidate) > 30 and "http" not in candidate[:10]:
                            snippet = candidate
                            break
                    break
            results.append({"title": title.strip(), "url": url, "content": snippet[:300]})
        return results
    except Exception:
        return []


def execute_search(query: str) -> str:
    """Execute a web search and return formatted results."""
    results = _search_ddg(query)
    if not results:
        return json.dumps({"error": "搜索暂不可用，请基于你的知识进行分析"})

    formatted = []
    for r in results:
        formatted.append(f"- [{r['title']}]({r['url']}): {r['content']}")
    return "\n".join(formatted)
