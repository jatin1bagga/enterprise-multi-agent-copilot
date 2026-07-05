from datetime import datetime, timedelta
from typing import Any

from app.db import crud
from app.db.base import SessionLocal
from app.graph.state import GraphState


def save_memory_node(state: GraphState) -> dict[str, Any]:
    conversation_id = state["conversation_id"]
    plan = state.get("plan") or []
    agent_trace = state.get("agent_trace") or []
    artifacts = state.get("artifacts") or []

    with SessionLocal() as db:
        crud.add_message(db, conversation_id, role="user", content=state["user_query"])

        assistant_message = crud.add_message(
            db,
            conversation_id,
            role="assistant",
            content=state.get("final_answer", ""),
            plan=plan,
            agent_trace=agent_trace,
        )

        for artifact in artifacts:
            crud.create_artifact(
                db,
                conversation_id=conversation_id,
                message_id=assistant_message.id,
                artifact_type=artifact["artifact_type"],
                file_path=artifact["file_path"],
                mime_type=artifact["mime_type"],
                title=artifact.get("title", artifact["artifact_type"]),
                metadata=artifact.get("metadata"),
            )

        now = datetime.utcnow()
        for trace in agent_trace:
            duration = timedelta(milliseconds=trace.get("duration_ms", 0))
            crud.record_agent_run(
                db,
                conversation_id=conversation_id,
                agent_name=trace["agent"],
                status=trace["status"],
                started_at=now - duration,
                finished_at=now,
                message_id=assistant_message.id,
            )

    return {}
