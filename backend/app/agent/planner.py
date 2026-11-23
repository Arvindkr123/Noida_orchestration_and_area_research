import json
from functools import lru_cache

from langchain_core.exceptions import OutputParserException
from langchain_groq import ChatGroq

from app.config import get_settings

from app.schemas.research import (
    ResearchIntent,
    ResearchPlan
)


# Reuse one client across requests instead of rebuilding it for every graph run.
@lru_cache
def get_llm():

    settings = get_settings()

    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0
    )


async def parse_user_intent(request: dict) -> ResearchIntent:

    llm = get_llm()

    # Validate the model's response against our schema before storing it in state.
    structured_llm = llm.with_structured_output(
        ResearchIntent,
        method="json_mode"
    )

    prompt = f"""
    You are an expert location research assistant.

    Research location: Noida, India.

    User selected mode: {request["mode"]}
    User input: {request["input"]}

    Extract:
    - City
    - Sector, if explicitly provided
    - Research topics
    - Whether current information is needed
    - User constraints
    - Original request

    Never invent a sector or location.
    Return only a JSON object with these exact keys:
    city (string), sector (string or null), topic (array of strings),
    time_sensitive (boolean), constraints (array of strings), and
    original_request (string).
    """

    # ainvoke is the async LangChain call; the parser returns a ResearchIntent.
    result = await structured_llm.ainvoke(prompt)

    return result


async def create_research_plan(
    intent: ResearchIntent
) -> ResearchPlan:

    llm = get_llm()

    # This stage proposes questions and tools; it does not execute the tools.
    structured_llm = llm.with_structured_output(
        ResearchPlan,
        method="json_mode"
    )

    prompt = f"""
    You are a senior research planning agent.

    User intent:
    {intent.model_dump_json(indent=2)}

    Available tools:

    news_search: Recent news and announcements.
    weather: Current weather and forecast.
    traffic: Traffic and connectivity information.

    Create 3 to 6 useful research questions.

    Select relevant tools.
    Include all three for broad area research.

    Do not claim tools have been executed.

    Return one JSON object matching this schema. All four properties must be
    at the top level. research_questions must contain only question strings;
    do not put property names, punctuation, or tool lists in that array.
    {json.dumps(ResearchPlan.model_json_schema(), indent=2)}
    """

    # JSON mode asks for JSON text; Pydantic then checks it against ResearchPlan.
    try:
        result = await structured_llm.ainvoke(prompt)
    except OutputParserException:
        # Retry only schema/JSON parsing failures; network and API errors still
        # propagate so callers can report the real failure.
        retry_prompt = f"""
        {prompt}

        The previous response did not match the schema. Return a new JSON
        object with location_scope, research_questions, selected_tools, and
        reasoning as sibling properties. Include 3 to 6 string values in
        research_questions. Keep selected_tools as a separate array containing
        only valid tool names.
        """
        result = await structured_llm.ainvoke(retry_prompt)

    return result
