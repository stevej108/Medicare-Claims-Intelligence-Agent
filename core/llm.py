import os

from langchain_ollama import ChatOllama


LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama",
)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b",
)


def get_llm():
    """
    Return the configured LLM for the claims intelligence agent.
    """

    if LLM_PROVIDER == "ollama":
        return ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.2,
        )

    raise ValueError(
        f"Unsupported LLM provider: {LLM_PROVIDER}"
    )