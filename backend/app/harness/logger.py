import logging


logger = logging.getLogger("app.harness")


def log_tool_event(run_id: str, tool: str, status: str) -> None:
    logger.info(
        "run_id=%s tool=%s status=%s",
        run_id,
        tool,
        status,
    )