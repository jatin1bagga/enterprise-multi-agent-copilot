import json
import logging
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_graph
from app.api.schemas.chat import ChatRequest
from app.db import crud
from app.db.base import SessionLocal
from app.graph.builder import GRAPH_NAME, _AGENT_NODES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["chat"])


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _stream_chat(graph: CompiledStateGraph, conversation_id: str, message: str) -> AsyncGenerator[str, None]:
    # Each turn gets its own checkpointer thread. Cross-turn memory is handled explicitly via
    # SQLite (load_memory_node), not via LangGraph's checkpoint persistence - reusing
    # conversation_id as the thread_id would carry the previous turn's plan/artifacts/outputs
    # (accumulated via additive reducers) into this turn, since the checkpointer resumes state
    # for a given thread_id rather than starting fresh.
    thread_id = f"{conversation_id}:{uuid.uuid4()}"
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "conversation_id": conversation_id,
        "user_query": message,
        "messages": [HumanMessage(content=message)],
    }

    final_output: dict = {}
    try:
        async for event in graph.astream_events(initial_state, config=config, version="v2"):
            kind = event["event"]
            name = event.get("name")
            data = event.get("data", {})

            if kind == "on_chat_model_stream" and event.get("metadata", {}).get("langgraph_node") == "synthesize":
                chunk = data.get("chunk")
                if chunk is not None and chunk.content:
                    yield _sse("token", {"content": chunk.content})
            elif kind == "on_chain_end" and name == "planner":
                output = data.get("output") or {}
                if "plan" in output:
                    yield _sse("plan", {"plan": output["plan"]})
            elif kind == "on_chain_end" and name in _AGENT_NODES:
                output = data.get("output") or {}
                status = "done" if output.get("agent_outputs") else "retrying_or_failed"
                yield _sse("agent_status", {"agent": name, "status": status})
            elif kind == "on_chain_end" and name == GRAPH_NAME:
                final_output = data.get("output") or {}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Chat stream failed for conversation %s", conversation_id)
        yield _sse("error", {"message": str(exc)})
        return

    citations = final_output.get("citations") or []
    artifact_dicts = final_output.get("artifacts") or []
    artifact_payload = []
    if artifact_dicts:
        with SessionLocal() as db:
            records = crud.list_artifacts(db, conversation_id)[-len(artifact_dicts):]
        artifact_payload = [
            {"id": r.id, "title": r.title, "type": r.artifact_type, "mime_type": r.mime_type}
            for r in records
        ]

    yield _sse(
        "final",
        {
            "content": final_output.get("final_answer", ""),
            "citations": citations,
            "artifacts": artifact_payload,
        },
    )


@router.post("/{conversation_id}/chat")
async def chat(
    conversation_id: str,
    payload: ChatRequest,
    db: Session = Depends(get_db_session),
    graph: CompiledStateGraph = Depends(get_graph),
) -> StreamingResponse:
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return StreamingResponse(
        _stream_chat(graph, conversation_id, payload.message),
        media_type="text/event-stream",
    )
