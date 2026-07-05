from app.agents.rag.schemas import Citation
from app.vectorstore.chroma_client import get_vector_store


def retrieve_chunks(conversation_id: str, query: str, k: int = 5) -> list[Citation]:
    store = get_vector_store(conversation_id)
    results = store.similarity_search(query, k=k)

    citations: list[Citation] = []
    for doc in results:
        meta = doc.metadata
        citations.append(
            Citation(
                source_file=meta.get("source_file", "unknown"),
                page=meta.get("page", 0),
                chunk_index=meta.get("chunk_index", 0),
                snippet=doc.page_content[:400],
            )
        )
    return citations
