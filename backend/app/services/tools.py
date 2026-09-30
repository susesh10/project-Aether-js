import httpx
from datetime import datetime
from zoneinfo import ZoneInfo

# Change if you want a fixed zone; otherwise system local is used
DEFAULT_TZ = "Asia/Kolkata"


def get_current_time() -> dict:
    """Return current local time, date, and rough season."""
    if DEFAULT_TZ:
        now = datetime.now(ZoneInfo(DEFAULT_TZ))
        tz_name = DEFAULT_TZ
    else:
        now = datetime.now().astimezone()
        tz_name = str(now.tzinfo) if now.tzinfo else "local"

    month = now.month
    if month in (12, 1, 2):
        season = "winter"
    elif month in (3, 4, 5):
        season = "spring"
    elif month in (6, 7, 8):
        season = "summer"
    else:
        season = "autumn"

    return {
        "iso": now.isoformat(timespec="seconds"),
        "date": now.strftime("%A, %B %d, %Y"),
        "time": now.strftime("%I:%M %p").lstrip("0"),
        "timezone": tz_name,
        "season": season,
        "hour_24": now.hour,
    }
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