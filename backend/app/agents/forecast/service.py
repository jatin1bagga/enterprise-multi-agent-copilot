import numpy as np
import pandas as pd

_PERIOD_KEYWORDS = ("date", "time", "month", "quarter", "year", "week", "period", "day")


def _find_period_column(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if any(kw in col.lower() for kw in _PERIOD_KEYWORDS):
            return col
    return None


def _find_metric_column(df: pd.DataFrame, instruction: str) -> str | None:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        return None
    instruction_lower = instruction.lower()
    for col in numeric_cols:
        if col.lower() in instruction_lower:
            return col
    non_id_cols = [c for c in numeric_cols if "id" not in c.lower()]
    return (non_id_cols or numeric_cols)[0]


def compute_forecast(df: pd.DataFrame, instruction: str, periods_ahead: int) -> dict:
    metric_col = _find_metric_column(df, instruction)
    if metric_col is None:
        raise ValueError("No numeric column was found in the uploaded data to forecast.")

    period_col = _find_period_column(df)

    if period_col:
        series = df.groupby(period_col, sort=False)[metric_col].sum(min_count=1).dropna()
        try:
            sort_order = np.argsort(pd.to_datetime(series.index, errors="raise").to_numpy())
            series = series.iloc[sort_order]
        except (ValueError, TypeError):
            pass  # not date-like; keep first-appearance order
        periods = [str(p) for p in series.index]
        values = series.to_numpy(dtype=float)
    else:
        values = df[metric_col].dropna().to_numpy(dtype=float)
        periods = [f"Row {i + 1}" for i in range(len(values))]

    if len(values) < 2:
        raise ValueError(
            f"Not enough data points for '{metric_col}' to compute a trend (found {len(values)}, need at least 2)."
        )

    x = np.arange(len(values))
    slope, intercept = np.polyfit(x, values, 1)
    predicted = slope * x + intercept
    residual_std = float(np.std(values - predicted)) if len(values) > 2 else 0.0
    margin = 1.28 * residual_std  # ~80% band around a simple linear trend

    future_x = np.arange(len(values), len(values) + periods_ahead)
    future_values = slope * future_x + intercept

    trend_direction = "flat" if abs(slope) < 1e-9 else ("increasing" if slope > 0 else "decreasing")

    return {
        "metric_column": metric_col,
        "period_column": period_col,
        "historical": [{"period": p, "value": float(v)} for p, v in zip(periods, values)],
        "forecast": [
            {
                "period": f"Forecast +{i + 1}",
                "value": float(v),
                "lower": float(v - margin),
                "upper": float(v + margin),
            }
            for i, v in enumerate(future_values)
        ],
        "trend_direction": trend_direction,
        "slope_per_period": float(slope),
    }
