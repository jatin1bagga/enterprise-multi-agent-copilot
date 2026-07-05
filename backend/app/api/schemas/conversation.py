from datetime import datetime

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    title: str = "New conversation"


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
