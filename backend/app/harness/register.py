from collections.abc import Awaitable, Callable
from typing import Any

from app.schemas.research import ResearchIntent, ResearchPlan, ToolName
from app.tools.news import search_news
from app.tools.traffic import search_traffic
from app.tools.weather import get_weather


ToolHandler = Callable[
    [ResearchIntent, ResearchPlan],
    Awaitable[dict[str, Any]],
]

TOOL_REGISTRY: dict[ToolName, ToolHandler] = {
    "news_search": search_news,
    "weather": get_weather,
    "traffic": search_traffic,
}