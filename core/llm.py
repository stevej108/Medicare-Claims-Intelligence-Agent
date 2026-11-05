import os

from langchain_ollama import ChatOllama


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)


def get_llm() -> ChatOllama:
    """
    Return the local LLM used by the claims intelligence agent.
    """

    return ChatOllama(
        model="qwen3:8b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.2,
    )