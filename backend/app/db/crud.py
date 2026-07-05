import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AgentRun, AnalysisArtifact, Conversation, Message, UploadedFile


def create_conversation(db: Session, title: str = "New conversation") -> Conversation:
    conversation = Conversation(title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(db: Session) -> list[Conversation]:
    return list(db.scalars(select(Conversation).order_by(Conversation.updated_at.desc())))


def get_conversation(db: Session, conversation_id: str) -> Conversation | None:
    return db.get(Conversation, conversation_id)


def touch_conversation(db: Session, conversation_id: str) -> None:
    conversation = db.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        db.commit()


def add_message(
    db: Session,
    conversation_id: str,
    role: str,
    content: str,
    plan: list[dict] | None = None,
    agent_trace: list[dict] | None = None,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        plan_json=json.dumps(plan) if plan is not None else None,
        agent_trace_json=json.dumps(agent_trace) if agent_trace is not None else None,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    touch_conversation(db, conversation_id)
    return message


def list_messages(db: Session, conversation_id: str, limit: int = 50) -> list[Message]:
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


def create_uploaded_file(
    db: Session,
    conversation_id: str,
    filename: str,
    stored_path: str,
    file_type: str,
    size_bytes: int,
) -> UploadedFile:
    record = UploadedFile(
        conversation_id=conversation_id,
        filename=filename,
        stored_path=stored_path,
        file_type=file_type,
        size_bytes=size_bytes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_file_status(
    db: Session, file_id: str, status: str, chroma_collection_name: str | None = None
) -> None:
    record = db.get(UploadedFile, file_id)
    if record:
        record.status = status
        if chroma_collection_name:
            record.chroma_collection_name = chroma_collection_name
        db.commit()


def list_files(db: Session, conversation_id: str) -> list[UploadedFile]:
    stmt = select(UploadedFile).where(UploadedFile.conversation_id == conversation_id)
    return list(db.scalars(stmt))


def create_artifact(
    db: Session,
    conversation_id: str,
    artifact_type: str,
    file_path: str,
    mime_type: str,
    title: str,
    message_id: str | None = None,
    metadata: dict | None = None,
) -> AnalysisArtifact:
    artifact = AnalysisArtifact(
        conversation_id=conversation_id,
        message_id=message_id,
        artifact_type=artifact_type,
        file_path=file_path,
        mime_type=mime_type,
        title=title,
        metadata_json=json.dumps(metadata) if metadata is not None else None,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


def get_artifact(db: Session, artifact_id: str) -> AnalysisArtifact | None:
    return db.get(AnalysisArtifact, artifact_id)


def list_artifacts(db: Session, conversation_id: str) -> list[AnalysisArtifact]:
    stmt = select(AnalysisArtifact).where(AnalysisArtifact.conversation_id == conversation_id)
    return list(db.scalars(stmt))


def record_agent_run(
    db: Session,
    conversation_id: str,
    agent_name: str,
    status: str,
    started_at: datetime,
    finished_at: datetime,
    message_id: str | None = None,
    input_data: dict | None = None,
    output_data: dict | None = None,
    error: str | None = None,
) -> AgentRun:
    duration_ms = (finished_at - started_at).total_seconds() * 1000
    run = AgentRun(
        conversation_id=conversation_id,
        message_id=message_id,
        agent_name=agent_name,
        status=status,
        input_json=json.dumps(input_data) if input_data is not None else None,
        output_json=json.dumps(output_data) if output_data is not None else None,
        error=error,
        duration_ms=duration_ms,
        started_at=started_at,
        finished_at=finished_at,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run
