import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.vectorstore.chroma_client import get_vector_store

logger = logging.getLogger(__name__)

_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


def ingest_pdf(file_path: str, conversation_id: str, file_id: str, filename: str) -> int:
    reader = PdfReader(file_path)
    store = get_vector_store(conversation_id)

    texts: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if not page_text.strip():
            continue
        chunks = _splitter.split_text(page_text)
        for chunk_index, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append(
                {
                    "source_file": filename,
                    "file_id": file_id,
                    "page": page_number,
                    "chunk_index": chunk_index,
                    "conversation_id": conversation_id,
                }
            )
            ids.append(f"{file_id}-p{page_number}-c{chunk_index}")

    if texts:
        store.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    logger.info("Ingested %d chunks from %s into conversation %s", len(texts), filename, conversation_id)
    return len(texts)
