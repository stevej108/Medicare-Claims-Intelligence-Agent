from functools import lru_cache

from rag.retriever import KnowledgeRetriever


@lru_cache(maxsize=1)
def get_retriever() -> KnowledgeRetriever:
    """
    Create and cache the local knowledge retriever.
    """

    return KnowledgeRetriever()


def knowledge_search(
    query: str,
    k: int = 3,
) -> dict:
    """
    Retrieve documentation relevant to a knowledge
    or methodology question.
    """

    if not query.strip():
        raise ValueError(
            "query cannot be empty."
        )

    retriever = get_retriever()

    results = retriever.retrieve(
        query=query,
        k=k,
    )

    return {
        "query": query,
        "results": results,
    }