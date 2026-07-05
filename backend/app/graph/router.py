from app.agents.base import current_step
from app.core.config import get_settings
from app.graph.state import GraphState


def route_from_planner(state: GraphState) -> str:
    plan = state.get("plan") or []
    idx = state.get("current_step_index", 0)
    if not plan or idx >= len(plan):
        return "synthesize"
    return plan[idx]["agent"]


def route_after_agent(state: GraphState) -> str:
    step = current_step(state)
    if step is None:
        return "planner"

    step_id = step["step_id"]
    if step_id in (state.get("agent_outputs") or {}):
        return "planner"

    settings = get_settings()
    retry_counts = state.get("retry_counts") or {}
    if retry_counts.get(step_id, 0) < settings.max_agent_retries:
        return step["agent"]
    return "planner"
