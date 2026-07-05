import functools
import logging
import time
import traceback
from collections.abc import Callable
from typing import Any, Protocol

from app.graph.state import GraphState

logger = logging.getLogger(__name__)


class AgentNode(Protocol):
    """Contract every agent graph-node callable follows: pure function of
    GraphState to a partial state update dict, merged by LangGraph's reducers."""

    def __call__(self, state: GraphState) -> dict[str, Any]: ...


def agent_node(name: str) -> Callable[[AgentNode], AgentNode]:
    """Wraps an agent node so exceptions become graph state (errors + retry_counts)
    instead of crashing the run, letting the router decide to retry or degrade gracefully."""

    def decorator(fn: AgentNode) -> AgentNode:
        @functools.wraps(fn)
        def wrapper(state: GraphState) -> dict[str, Any]:
            step = current_step(state)
            step_id = step["step_id"] if step else name
            started = time.monotonic()
            try:
                result = fn(state)
                duration_ms = (time.monotonic() - started) * 1000
                logger.info("agent=%s status=success duration_ms=%.1f", name, duration_ms)
                result.setdefault("agent_trace", []).append(
                    {"agent": name, "step_id": step_id, "status": "success", "duration_ms": duration_ms}
                )
                return result
            except Exception as exc:  # noqa: BLE001
                duration_ms = (time.monotonic() - started) * 1000
                logger.exception("agent=%s failed", name)
                retry_counts = dict(state.get("retry_counts", {}))
                retry_counts[step_id] = retry_counts.get(step_id, 0) + 1
                return {
                    "errors": [
                        {
                            "agent": name,
                            "step_id": step_id,
                            "error": str(exc),
                            "traceback": traceback.format_exc(),
                        }
                    ],
                    "retry_counts": retry_counts,
                    "agent_trace": [
                        {"agent": name, "step_id": step_id, "status": "failed", "duration_ms": duration_ms}
                    ],
                }

        return wrapper

    return decorator


def current_step(state: GraphState) -> dict | None:
    plan = state.get("plan") or []
    idx = state.get("current_step_index", 0)
    if 0 <= idx < len(plan):
        return plan[idx]
    return None
