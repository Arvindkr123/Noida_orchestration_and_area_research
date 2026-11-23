import asyncio
import logging
from typing import Any

from app.agent.state import ResearchState
from app.harness.logger import log_tool_event
from app.harness.register import TOOL_REGISTRY
from app.harness.validation import (
    ToolExecutionResult,
    validate_tool_result,
)
from app.schemas.research import ResearchIntent, ResearchPlan


logger = logging.getLogger(__name__)


async def _execute_one(
    run_id: str,
    tool_name: str,
    intent: ResearchIntent,
    plan: ResearchPlan,
) -> ToolExecutionResult:
    # Isolate each tool's error so one provider failure does not cancel the others.
    log_tool_event(run_id, tool_name, "started")
    try:
        data = await TOOL_REGISTRY[tool_name](intent, plan)
        result = validate_tool_result(tool_name, data)
    except Exception as error:
        log_tool_event(run_id, tool_name, "failed")
        logger.exception(
            "run_id=%s tool=%s execution_failed",
            run_id,
            tool_name,
        )
        message = str(error).strip() or type(error).__name__
        return ToolExecutionResult(
            tool=tool_name,
            status="error",
            error=message,
        )

    log_tool_event(run_id, tool_name, "completed")
    return result


async def execute_selected_tools(
    state: ResearchState,
    intent: ResearchIntent,
    plan: ResearchPlan,
) -> dict[str, Any]:
    """Run each planned tool once and retain individual failures in the output."""
    run_id = state["run_id"]
    # gather runs the selected async tools concurrently and preserves their order.
    results = await asyncio.gather(
        *(
            _execute_one(run_id, tool_name, intent, plan)
            for tool_name in plan.selected_tools
        )
    )
    # Convert Pydantic results to dictionaries before storing them in graph state.
    serialized = [result.model_dump() for result in results]
    errors = [
        f"{result.tool}: {result.error}"
        for result in results
        if result.status == "error"
    ]

    return {
        "tool_results": serialized,
        "errors": errors,
        "trace": [
            f"{result.tool}_{'completed' if result.status == 'success' else 'failed'}"
            for result in results
        ],
    }