from langchain_ollama import ChatOllama

def get_llm() -> ChatOllama:
    """
    Return the local LLM used by the claim intelligence agent.
    """

    return ChatOllama(
        model= "qwen3:8b",
        temperature= 0.2
    )