from sentence_transformers import (
    SentenceTransformer,
)


EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


def get_embedding_model() -> SentenceTransformer:
    """
    Return the local embedding model used for semantic
    retrieval.
    """

    return SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )
