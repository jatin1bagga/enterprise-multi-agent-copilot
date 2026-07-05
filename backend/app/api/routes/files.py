import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.agents.rag.ingest import ingest_pdf
from app.api.deps import get_db_session
from app.api.schemas.file import FileOut
from app.core.config import get_settings
from app.db import crud
from app.utils.files import infer_file_type
from app.utils.ids import new_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["files"])


@router.post("/{conversation_id}/files", response_model=FileOut)
async def upload_file(
    conversation_id: str, file: UploadFile, db: Session = Depends(get_db_session)
) -> FileOut:
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    settings = get_settings()
    file_type = infer_file_type(file.filename)
    if file_type not in ("pdf", "csv", "xlsx"):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")

    stored_name = f"{new_id()}_{file.filename}"
    stored_path = settings.upload_abs_dir / stored_name
    content = await file.read()
    stored_path.write_bytes(content)

    record = crud.create_uploaded_file(
        db,
        conversation_id=conversation_id,
        filename=file.filename,
        stored_path=str(stored_path),
        file_type=file_type,
        size_bytes=len(content),
    )

    if file_type == "pdf":
        try:
            chunk_count = ingest_pdf(str(stored_path), conversation_id, record.id, file.filename)
            crud.update_file_status(
                db, record.id, status="ingested" if chunk_count > 0 else "failed", chroma_collection_name=None
            )
            record.status = "ingested" if chunk_count > 0 else "failed"
        except Exception:
            logger.exception("PDF ingestion failed for %s", file.filename)
            crud.update_file_status(db, record.id, status="failed")
            record.status = "failed"
    else:
        crud.update_file_status(db, record.id, status="ingested")
        record.status = "ingested"

    return FileOut.model_validate(record)


@router.get("/{conversation_id}/files", response_model=list[FileOut])
def list_files(conversation_id: str, db: Session = Depends(get_db_session)) -> list[FileOut]:
    return [FileOut.model_validate(f) for f in crud.list_files(db, conversation_id)]
