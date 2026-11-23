
import logging

from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.schemas.research import ResearchRequest
from app.agent.graph import research_graph


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Research"]
)


@router.post("/research")
async def create_research(request: ResearchRequest):
    """Run the research graph and return its final state as an API response."""

    # Reuse this ID in logs and the response so a run is easy to trace.
    run_id = str(uuid4())

    logger.info(
        "run_id=%s mode=%s research_started",
        run_id,
        request.mode
    )

    # LangGraph passes this shared state through each node; later nodes fill
    # intent, plan, results, and trace entries.
    initial_state = {
        "run_id": run_id,
        # The graph fills in intent and plan as its nodes run.
        "request": request.model_dump(),
        "intent": {},
        "plan": {},
        "tool_results": [],
        "trace": [],
        "errors": []
    }

    try:
        # ainvoke waits for the graph to finish all its connected nodes.
        result = await research_graph.ainvoke(
            initial_state
        )

        return {
            "success": not result["errors"],
            "run_id": run_id,
            "status": (
                "completed_with_errors"
                if result["errors"]
                else "completed"
            ),
            "mode": request.mode,
            "intent": result["intent"],
            "research_plan": result["plan"],
            "tool_results": result["tool_results"],
            "errors": result["errors"],
            "execution_trace": result["trace"],
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

    except Exception as error:

        # A graph-level failure (for example, an invalid LLM plan) aborts the
        # run, so return an HTTP error instead of a partial-success response.
        logger.exception(
            "run_id=%s research_failed",
            run_id
        )

        raise HTTPException(
            status_code=502,
            detail={
                "message": "Research orchestration failed",
                "run_id": run_id,
                "error": str(error)
            }
        )
