import uuid


def new_id(prefix: str = "") -> str:
    suffix = uuid.uuid4().hex[:12]
    return f"{prefix}{suffix}" if prefix else suffix
