import logging
import uuid

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.planner.prompts import PLANNER_SYSTEM_PROMPT, build_context_block
from app.agents.planner.schemas import ExecutionPlan
from app.graph.state import PlannedStep
from app.llm.factory import get_chat_model

logger = logging.getLogger(__name__)


def build_plan(user_query: str, context: dict) -> list[PlannedStep]:
    llm = get_chat_model(temperature=0.0)
    structured_llm = llm.with_structured_output(ExecutionPlan)

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"{build_context_block(context)}\n\nUser request: {user_query}"),
    ]

    try:
        plan: ExecutionPlan = structured_llm.invoke(messages)
    except Exception:
        logger.exception("Planner structured output failed; falling back to no-agent plan")
        return []

    steps: list[PlannedStep] = []
    for step in plan.steps:
        steps.append(
            PlannedStep(
                step_id=step.step_id or f"s{uuid.uuid4().hex[:6]}",
                agent=step.agent,
                instruction=step.instruction,
                depends_on=step.depends_on,
                status="pending",
            )
        )
    return steps
