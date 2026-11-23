
import operator

from typing import Any, TypedDict, Annotated


class ResearchState(TypedDict):
    """Data shared between nodes while one LangGraph run is in progress."""

    run_id: str

    request: dict

    intent: dict

    plan: dict

    # operator.add is a reducer: when a node returns more entries, append them.
    tool_results: Annotated[list[dict[str, Any]], operator.add]

    trace: Annotated[list[str], operator.add]

    errors: Annotated[list[str], operator.add]
