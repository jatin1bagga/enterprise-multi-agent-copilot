from typing import Any

from app.agents.memory.service import load_context
from app.db.base import SessionLocal
from app.graph.state import GraphState


def load_memory_node(state: GraphState) -> dict[str, Any]:
    with SessionLocal() as db:
        context = load_context(db, state["conversation_id"])
    return {"context": context}
