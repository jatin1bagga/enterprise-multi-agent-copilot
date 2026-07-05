from functools import lru_cache

import chromadb
from langchain_chroma import Chroma

from app.core.config import get_settings
from app.llm.factory import get_embeddings


@lru_cache
def get_chroma_client() -> chromadb.ClientAPI:
    settings = get_settings()
    return chromadb.PersistentClient(path=str(settings.chroma_abs_dir))


def collection_name_for(conversation_id: str) -> str:
    return f"session_{conversation_id}".replace("-", "")


def get_vector_store(conversation_id: str) -> Chroma:
    client = get_chroma_client()
    return Chroma(
        client=client,
        collection_name=collection_name_for(conversation_id),
        embedding_function=get_embeddings(),
    )
