from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.api.schemas.conversation import ConversationCreate, ConversationOut, MessageOut
from app.db import crud

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut)
def create_conversation(payload: ConversationCreate, db: Session = Depends(get_db_session)) -> ConversationOut:
    conversation = crud.create_conversation(db, title=payload.title)
    return ConversationOut.model_validate(conversation)


@router.get("", response_model=list[ConversationOut])
def list_conversations(db: Session = Depends(get_db_session)) -> list[ConversationOut]:
    return [ConversationOut.model_validate(c) for c in crud.list_conversations(db)]


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def get_messages(conversation_id: str, db: Session = Depends(get_db_session)) -> list[MessageOut]:
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return [MessageOut.model_validate(m) for m in crud.list_messages(db, conversation_id, limit=500)]
