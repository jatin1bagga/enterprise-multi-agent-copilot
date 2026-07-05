from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import Settings, get_settings


@lru_cache
def get_chat_model(temperature: float = 0.1) -> BaseChatModel:
    settings = get_settings()
    return _build_chat_model(settings, temperature)


def _build_chat_model(settings: Settings, temperature: float) -> BaseChatModel:
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=temperature,
        )
    if settings.llm_provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=temperature,
        )

    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=temperature,
    )


@lru_cache
def get_embeddings() -> Embeddings:
    settings = get_settings()

    if settings.llm_provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(api_key=settings.openai_api_key)
    if settings.llm_provider == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", google_api_key=settings.gemini_api_key
        )

    from langchain_ollama import OllamaEmbeddings

    return OllamaEmbeddings(model=settings.ollama_embed_model, base_url=settings.ollama_base_url)
