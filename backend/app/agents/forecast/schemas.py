from pydantic import BaseModel


class ForecastPoint(BaseModel):
    period: str
    value: float
    lower: float | None = None
    upper: float | None = None


class ForecastResult(BaseModel):
    metric_column: str
    period_column: str | None
    historical: list[ForecastPoint]
    forecast: list[ForecastPoint]
    trend_direction: str
    narrative: str
