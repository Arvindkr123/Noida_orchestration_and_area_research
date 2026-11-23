from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


# Only these tool identifiers can be returned by a research plan.
ToolName = Literal[
    "news_search",
    "weather",
    "traffic"
]


# Only these request modes are accepted by the API.
ResearchMode = Literal[
    "query",
    "sector",
    "city"
]


class ResearchRequest(BaseModel):
    """Validated request body accepted by POST /api/research."""

    mode: ResearchMode
    input: str = Field(
        ...,
         min_length=2,
        max_length=500,
        description="Research query, sector name or city name"
    )
    
    @field_validator("input")
    @classmethod
    def validate_input(cls, value):

        # Normalize whitespace before applying the mode-specific checks.
        value = value.strip()

        if not value:
            raise ValueError("Input cannot be empty")

        return value

    @model_validator(mode="after")
    def validate_mode_input(self):

        # This prototype intentionally limits city-level research to Noida.
        if self.mode == "city":
            if self.input.lower() != "noida":
                raise ValueError(
                    "For this assignment, city mode supports Noida only."
                )

        if self.mode == "sector":
            # Avoid sending a sector request with no actual sector identifier.
            if "sector" not in self.input.lower():
                raise ValueError(
                    "Please provide a sector, e.g. Sector 62."
                )

        return self
    

class ResearchIntent(BaseModel):
    """Normalized location and topics extracted from the user's request."""

    city: str = "Noida"

    sector: str | None = None

    topic: list[str] = Field(default_factory=list)

    time_sensitive: bool = True

    constraints: list[str] = Field(default_factory=list)

    original_request: str


class ResearchPlan(BaseModel):
    """Questions and registered tools proposed for one research run."""

    location_scope: str

    research_questions: list[str]

    # Restricting this field to ToolName prevents arbitrary tool dispatch.
    selected_tools: list[ToolName]

    reasoning: str