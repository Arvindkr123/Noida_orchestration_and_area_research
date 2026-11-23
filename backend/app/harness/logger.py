import logging


logger = logging.getLogger("app.harness")


def log_tool_event(run_id: str, tool: str, status: str) -> None:
    """Write a consistent start/completion/failure event for one tool."""
    logger.info(
        "run_id=%s tool=%s status=%s",
        run_id,
        tool,
        status,
    )