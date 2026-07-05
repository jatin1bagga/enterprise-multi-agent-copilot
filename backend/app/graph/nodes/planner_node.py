from typing import Any

from app.agents.planner.service import build_plan
from app.graph.state import GraphState


def planner_node(state: GraphState) -> dict[str, Any]:
    if "plan" not in state:
        plan = build_plan(state["user_query"], state.get("context", {}))
        return {"plan": plan, "current_step_index": 0}

    plan = [dict(step) for step in state["plan"]]
    idx = state.get("current_step_index", 0)

    if 0 <= idx < len(plan):
        step = plan[idx]
        step["status"] = "done" if step["step_id"] in (state.get("agent_outputs") or {}) else "failed"
        idx += 1

    return {"plan": plan, "current_step_index": idx}
