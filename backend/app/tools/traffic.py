from typing import Any

from app.schemas.research import ResearchIntent, ResearchPlan
from app.tools.tavily import tavily_search


async def search_traffic(
    intent: ResearchIntent,
    _plan: ResearchPlan,
) -> dict[str, Any]:
    """Search the web for current traffic and connectivity information."""
    location = intent.sector or intent.city
    query = (
        f"Current traffic conditions, congestion, road closures, and "
        f"public transport around {location}, Noida"
    )

    return await tavily_search(query, topic="general")