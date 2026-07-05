import logging
import logging.config
from pathlib import Path

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "default",
                    "filename": str(log_dir / "app.log"),
                    "maxBytes": 5_000_000,
                    "backupCount": 3,
                },
            },
            "root": {
                "level": settings.log_level,
                "handlers": ["console", "file"],
            },
            "loggers": {
                "watchfiles": {"level": "WARNING"},
                "httpx": {"level": "WARNING"},
            },
        }
    )
