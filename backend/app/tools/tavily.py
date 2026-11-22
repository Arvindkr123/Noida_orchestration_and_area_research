from typing import Any

import httpx

from app.config import get_settings


TAVILY_SEARCH_URL = "https://api.tavily.com/search"


async def tavily_search(query: str, *, topic: str) -> dict[str, Any]:
    """Run one Tavily search and return a small, consistent result payload."""
    settings = get_settings()

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            TAVILY_SEARCH_URL,
            json={
                "api_key": settings.TAVILY_API_KEY,
                "query": query,
                "topic": topic,
                "search_depth": "basic",
                "max_results": 5,
                "include_answer": True,
            },
        )
        response.raise_for_status()
        payload = response.json()

    if not isinstance(payload, dict) or not isinstance(
        payload.get("results"), list
    ):
        raise ValueError("Tavily returned an invalid search response")

    results = []
    for item in payload["results"]:
        if not isinstance(item, dict):
            raise ValueError("Tavily returned a malformed search result")
        title = item.get("title")
        url = item.get("url")
        content = item.get("content")
        required_fields = (title, url, content)
        if not all(
            isinstance(value, str) and value.strip()
            for value in required_fields
        ):
            raise ValueError("Tavily returned a search result without its required fields")
        results.append(
            {
                "title": title,
                "url": url,
                "content": content,
                "published_date": item.get("published_date"),
                "score": item.get("score"),
            }
        )

    return {
        "provider": "Tavily",
        "query": query,
        "answer": payload.get("answer"),
        "results": results,
    }
