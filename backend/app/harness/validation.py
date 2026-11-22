from typing import Any, Literal

from pydantic import BaseModel, model_validator

from app.schemas.research import ResearchPlan, ToolName


class ToolExecutionResult(BaseModel):
    tool: ToolName
    status: Literal["success", "error"]
    data: dict[str, Any] | None = None
    error: str | None = None

    @model_validator(mode="after")
    def validate_status_fields(self):
        if self.status == "success":
            if self.data is None or self.error is not None:
                raise ValueError(
                    "Successful tool results need data and cannot contain an error"
                )
        elif not self.error:
            raise ValueError("Failed tool results need an error message")

        return self


def validate_research_plan(plan: ResearchPlan | dict[str, Any]) -> ResearchPlan:
    """Validate both the plan's shape and the constraints in the planning prompt."""
    validated = ResearchPlan.model_validate(plan)
    questions = [question.strip() for question in validated.research_questions]

    if not 3 <= len(questions) <= 6:
        raise ValueError("A research plan must contain between 3 and 6 questions")
    if any(not question for question in questions):
        raise ValueError("Research questions cannot be empty")
    if len({question.casefold() for question in questions}) != len(questions):
        raise ValueError("Research questions must be unique")
    if not validated.selected_tools:
        raise ValueError("A research plan must select at least one tool")
    if len(set(validated.selected_tools)) != len(validated.selected_tools):
        raise ValueError("A research plan cannot select the same tool more than once")

    return validated


def validate_tool_result(
    tool: ToolName,
    data: dict[str, Any],
) -> ToolExecutionResult:
    return ToolExecutionResult(tool=tool, status="success", data=data)