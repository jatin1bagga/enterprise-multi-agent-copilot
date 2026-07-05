from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.api.schemas.artifact import ArtifactOut
from app.db import crud

router = APIRouter(prefix="/api/artifacts", tags=["artifacts"])


@router.get("/{artifact_id}/download")
def download_artifact(artifact_id: str, db: Session = Depends(get_db_session)) -> FileResponse:
    artifact = crud.get_artifact(db, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(path=artifact.file_path, media_type=artifact.mime_type, filename=artifact.title)


@router.get("/conversations/{conversation_id}", response_model=list[ArtifactOut])
def list_conversation_artifacts(conversation_id: str, db: Session = Depends(get_db_session)) -> list[ArtifactOut]:
    return [ArtifactOut.model_validate(a) for a in crud.list_artifacts(db, conversation_id)]
