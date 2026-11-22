
import operator

from typing import Any, TypedDict, Annotated


class ResearchState(TypedDict):

    run_id: str

    request: dict

    intent: dict

    plan: dict

    tool_results: Annotated[list[dict[str, Any]], operator.add]

    # LangGraph appends each node's updates instead of replacing earlier entries.
    trace: Annotated[list[str], operator.add]

    errors: Annotated[list[str], operator.add]
