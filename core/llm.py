import os

from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama


LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama",
).lower()

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b",
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    ""
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
)


def get_llm():

    if LLM_PROVIDER == "ollama":
        return ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.2,
        )

    if LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is required when "
                "LLM_PROVIDER=groq."
            )

        if not GROQ_MODEL:
            raise ValueError(
                "GROQ_MODEL is required when "
                "LLM_PROVIDER=groq."
            )

        return ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.2,
        )

    raise ValueError(
        f"Unsupported LLM provider: {LLM_PROVIDER}"
    )