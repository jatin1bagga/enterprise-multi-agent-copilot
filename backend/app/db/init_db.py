from app.db import models  # noqa: F401  (ensures models are registered on Base)
from app.db.base import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
