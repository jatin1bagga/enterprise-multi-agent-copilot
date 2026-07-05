from pathlib import Path

from app.core.config import get_settings


def artifact_path(filename: str) -> Path:
    settings = get_settings()
    return settings.artifact_abs_dir / filename


def upload_path(filename: str) -> Path:
    settings = get_settings()
    return settings.upload_abs_dir / filename


def infer_file_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower().lstrip(".")
    if suffix in ("xlsx", "xls"):
        return "xlsx"
    if suffix == "csv":
        return "csv"
    if suffix == "pdf":
        return "pdf"
    return suffix or "unknown"


def find_latest_tabular_file(context: dict) -> dict | None:
    files = context.get("uploaded_files", [])
    tabular = [f for f in files if f["file_type"] in ("csv", "xlsx") and f["status"] != "failed"]
    return tabular[-1] if tabular else None
