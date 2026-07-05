from pydantic import BaseModel


class ReportResult(BaseModel):
    markdown_path: str
    pdf_path: str
    pptx_path: str
