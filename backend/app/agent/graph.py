
import logging

from langgraph.graph import StateGraph, START, END

from app.agent.state import ResearchState
from app.harness.executor import execute_selected_tools
from app.harness.validation import validate_research_plan
from app.schemas.research import ResearchIntent, ResearchPlan

from app.agent.planner import (
    parse_user_intent,
    create_research_plan
)


logger = logging.getLogger(__name__)


# A node receives the current state and returns only the fields it updates.
async def intent_parser_node(state: ResearchState):

    run_id = state["run_id"]

    logger.info(
        "run_id=%s stage=intent_parser status=started",
        run_id
    )

    intent = await parse_user_intent(state["request"])

    logger.info(
        "run_id=%s stage=intent_parser status=completed",
        run_id
    )

    return {
        "intent": intent.model_dump(),
        "trace": ["intent_parsing_completed"]
    }


async def research_planner_node(state: ResearchState):

    run_id = state["run_id"]

    logger.info(
        "run_id=%s stage=research_planner status=started",
        run_id
    )

    # The graph stores plain dictionaries; rebuild the Pydantic model so this
    # node receives validated, typed intent data.
    intent = ResearchIntent(**state["intent"])

    plan = validate_research_plan(await create_research_plan(intent))

    logger.info(
        "run_id=%s stage=research_planner status=completed",
        run_id
    )

    return {
        "plan": plan.model_dump(),
        "trace": ["research_plan_created"]
    }


async def tool_executor_node(state: ResearchState):
    # Convert graph dictionaries back to typed models before calling the tools.
    intent = ResearchIntent(**state["intent"])
    plan = ResearchPlan(**state["plan"])
    return await execute_selected_tools(state, intent, plan)


def build_research_graph():

    # StateGraph connects our Python functions into a stateful workflow.
    workflow = StateGraph(ResearchState)

    workflow.add_node(
        "intent_parser",
        intent_parser_node
    )

    workflow.add_node(
        "research_planner",
        research_planner_node
    )
    workflow.add_node(
        "tool_executor",
        tool_executor_node
    )

    # These edges determine the order in which the three nodes run.
    workflow.add_edge(
        START,
        "intent_parser"
    )

    workflow.add_edge(
        "intent_parser",
        "research_planner"
    )

    workflow.add_edge(
        "research_planner",
        "tool_executor"
    )

    workflow.add_edge(
        "tool_executor",
        END
    )

    # Compile once at startup; each request invokes this reusable graph.
    return workflow.compile()


research_graph = build_research_graph()
