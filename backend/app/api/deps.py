from collections.abc import Generator

from fastapi import Request
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.orm import Session

from app.db.base import SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_graph(request: Request) -> CompiledStateGraph:
    return request.app.state.graph
