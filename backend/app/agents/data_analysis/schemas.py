from pydantic import BaseModel


class DataAnalysisResult(BaseModel):
    source_file: str
    eda: dict
    insights: str
