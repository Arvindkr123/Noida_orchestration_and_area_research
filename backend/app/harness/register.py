from collections.abc import Awaitable, Callable
from typing import Any

from app.schemas.research import ResearchIntent, ResearchPlan, ToolName
from app.tools.news import search_news
from app.tools.traffic import search_traffic
from app.tools.weather import get_weather


# A tool handler always accepts the same typed context and returns a data dict.
ToolHandler = Callable[
    [ResearchIntent, ResearchPlan],
    Awaitable[dict[str, Any]],
]

# This is the allowlist that maps LLM-selected names to real Python functions.
TOOL_REGISTRY: dict[ToolName, ToolHandler] = {
    "news_search": search_news,
    "weather": get_weather,
    "traffic": search_traffic,
}