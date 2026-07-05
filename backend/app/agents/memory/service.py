from sqlalchemy.orm import Session

from app.db import crud


def load_context(db: Session, conversation_id: str) -> dict:
    messages = crud.list_messages(db, conversation_id)
    files = crud.list_files(db, conversation_id)
    artifacts = crud.list_artifacts(db, conversation_id)

    return {
        "recent_messages": [{"role": m.role, "content": m.content} for m in messages],
        "uploaded_files": [
            {
                "id": f.id,
                "filename": f.filename,
                "file_type": f.file_type,
                "status": f.status,
                "stored_path": f.stored_path,
            }
            for f in files
        ],
        "prior_artifacts": [
            {"id": a.id, "artifact_type": a.artifact_type, "title": a.title, "file_path": a.file_path}
            for a in artifacts
        ],
    }


def save_turn(
    db: Session,
    conversation_id: str,
    user_query: str,
    final_answer: str,
    plan: list[dict],
    agent_trace: list[dict],
) -> None:
    crud.add_message(db, conversation_id, role="user", content=user_query)
    crud.add_message(
        db,
        conversation_id,
        role="assistant",
        content=final_answer,
        plan=plan,
        agent_trace=agent_trace,
    )
