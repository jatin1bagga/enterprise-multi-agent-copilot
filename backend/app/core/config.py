from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    llm_provider: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b-instruct"
    ollama_embed_model: str = "nomic-embed-text"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"

    data_dir: str = "data"
    sqlite_path: str = "data/app.db"
    chroma_dir: str = "data/chroma"
    upload_dir: str = "data/uploads"
    artifact_dir: str = "data/artifacts"

    sandbox_timeout_seconds: int = 30
    sandbox_memory_limit_mb: int = 512
    max_agent_retries: int = 2

    cors_origins: str = "http://localhost:3000"

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_address: str | None = None
    smtp_use_tls: bool = True

    forecast_periods_ahead: int = 3

    @property
    def smtp_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_from_address)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sqlite_url(self) -> str:
        return f"sqlite:///{self.sqlite_abs_path}"

    @property
    def sqlite_abs_path(self) -> Path:
        return (BACKEND_ROOT / self.sqlite_path).resolve()

    @property
    def chroma_abs_dir(self) -> Path:
        return (BACKEND_ROOT / self.chroma_dir).resolve()

    @property
    def upload_abs_dir(self) -> Path:
        return (BACKEND_ROOT / self.upload_dir).resolve()

    @property
    def artifact_abs_dir(self) -> Path:
        return (BACKEND_ROOT / self.artifact_dir).resolve()

    def ensure_directories(self) -> None:
        for path in (
            self.sqlite_abs_path.parent,
            self.chroma_abs_dir,
            self.upload_abs_dir,
            self.artifact_abs_dir,
            BACKEND_ROOT / "logs",
        ):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
