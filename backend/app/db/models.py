import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String, default="New conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    files: Mapped[list["UploadedFile"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    artifacts: Mapped[list["AnalysisArtifact"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    agent_runs: Mapped[list["AgentRun"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str] = mapped_column(String)  # user | assistant | system
    content: Mapped[str] = mapped_column(Text)
    plan_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent_trace_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    filename: Mapped[str] = mapped_column(String)
    stored_path: Mapped[str] = mapped_column(String)
    file_type: Mapped[str] = mapped_column(String)  # pdf | csv | xlsx
    size_bytes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default="uploaded")  # uploaded | ingested | failed
    chroma_collection_name: Mapped[str | None] = mapped_column(String, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped[Conversation] = relationship(back_populates="files")


class AnalysisArtifact(Base):
    __tablename__ = "analysis_artifacts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    message_id: Mapped[str | None] = mapped_column(ForeignKey("messages.id"), nullable=True)
    artifact_type: Mapped[str] = mapped_column(String)  # plot | table | report_md | report_pdf | report_pptx | code
    file_path: Mapped[str] = mapped_column(String)
    mime_type: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped[Conversation] = relationship(back_populates="artifacts")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    message_id: Mapped[str | None] = mapped_column(ForeignKey("messages.id"), nullable=True)
    agent_name: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)  # success | failed | retried
    input_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    conversation: Mapped[Conversation] = relationship(back_populates="agent_runs")
