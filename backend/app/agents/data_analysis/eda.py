from pathlib import Path

import pandas as pd


def load_tabular_file(path: str) -> pd.DataFrame:
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    raise ValueError(f"Unsupported tabular file type: {suffix}")


def run_eda(df: pd.DataFrame) -> dict:
    numeric_df = df.select_dtypes(include="number")

    missing = df.isna().sum()
    missing_pct = (missing / max(len(df), 1) * 100).round(2)

    correlations = {}
    if numeric_df.shape[1] >= 2:
        corr = numeric_df.corr(numeric_only=True).round(3)
        correlations = corr.to_dict()

    return {
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {
            col: {"count": int(missing[col]), "pct": float(missing_pct[col])}
            for col in df.columns
            if missing[col] > 0
        },
        "numeric_summary": numeric_df.describe().round(3).to_dict() if not numeric_df.empty else {},
        "correlations": correlations,
    }
