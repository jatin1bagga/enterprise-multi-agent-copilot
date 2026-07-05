from pydantic import BaseModel


class Citation(BaseModel):
    source_file: str
    page: int
    chunk_index: int
    snippet: str


class RagResult(BaseModel):
    answer: str
    citations: list[Citation]
