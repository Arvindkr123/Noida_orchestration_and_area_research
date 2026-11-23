from typing import Any

from app.schemas.research import ResearchIntent, ResearchPlan
from app.tools.tavily import tavily_search


async def search_news(
    intent: ResearchIntent,
    _plan: ResearchPlan,
) -> dict[str, Any]:
    """Find recent news relevant to the requested Noida location and topic."""
    # Prefer the explicitly extracted sector; otherwise search across the city.
    location = intent.sector or intent.city
    topics = ", ".join(intent.topic)
    query = f"Recent news and announcements about {location}, Noida"
    if topics:
        query = f"{query}: {topics}"

    # Tavily's news topic narrows the search to recent news and announcements.
    return await tavily_search(query, topic="news")