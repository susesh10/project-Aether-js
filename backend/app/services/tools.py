import httpx

SEARXNG_URL = "http://127.0.0.1:8888/search"

def web_search(query: str, max_results: int = 5) -> list[dict]:
    if not query or not query.strip():
        return []

    query = query.strip()

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                SEARXNG_URL,
                params={
                    "q": query,
                    "format": "json",
                    "language": "en-US",
                },
            )
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        print("web_search (SearxNG) error:", e)
        return []

    results = []
    for item in data.get("results", [])[:max_results]:
        results.append({
            "title": item.get("title", ""),
            "snippet": item.get("content", "") or item.get("snippet", ""),
            "url": item.get("url", ""),
        })

    return results