import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import artifacts, chat, conversations, files, health
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.init_db import init_db
from app.graph.builder import build_graph

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings)
    init_db()
    app.state.graph = await build_graph(settings)
    logger.info("Application startup complete (llm_provider=%s)", settings.llm_provider)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Enterprise Multi-Agent Operations Copilot", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(conversations.router)
    app.include_router(files.router)
    app.include_router(chat.router)
    app.include_router(artifacts.router)

    return app


app = create_app()
