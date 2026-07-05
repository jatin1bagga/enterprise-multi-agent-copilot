from datetime import datetime

from pydantic import BaseModel


class FileOut(BaseModel):
    id: str
    filename: str
    file_type: str
    size_bytes: int
    status: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}
