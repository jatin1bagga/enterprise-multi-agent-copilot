from datetime import datetime

from pydantic import BaseModel


class ArtifactOut(BaseModel):
    id: str
    artifact_type: str
    title: str
    mime_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
