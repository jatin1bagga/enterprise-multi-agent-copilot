import logging

import httpx
from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health(settings: Settings = Depends(get_settings)) -> dict:
    ollama_status = "unreachable"
    if settings.llm_provider == "ollama":
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{settings.ollama_base_url}/api/tags")
                resp.raise_for_status()
                models = [m["name"] for m in resp.json().get("models", [])]
                ollama_status = "reachable" if settings.ollama_model in models else "reachable (model not pulled)"
        except Exception as exc:  # noqa: BLE001
            logger.warning("Ollama health check failed: %s", exc)
            ollama_status = "unreachable"
    else:
        ollama_status = "n/a"

    return {
        "status": "ok",
        "app_env": settings.app_env,
        "llm_provider": settings.llm_provider,
        "model": settings.ollama_model if settings.llm_provider == "ollama" else settings.openai_model,
        "ollama": ollama_status,
    }
