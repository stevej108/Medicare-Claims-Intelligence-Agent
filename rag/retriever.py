import faiss
import numpy as np

from rag.documents import (
    load_markdown_documents,
)

from rag.embeddings import (
    get_embedding_model,
)


class KnowledgeRetriever:

    def __init__(self):
        self.documents = (
            load_markdown_documents()
        )

        self.embedding_model = (
            get_embedding_model()
        )

        texts = [
            document["text"]
            for document in self.documents
        ]

        embeddings = (
            self.embedding_model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        )

        embeddings = embeddings.astype(
            np.float32
        )

        dimension = embeddings.shape[1]

        self.index = (
            faiss.IndexFlatIP(
                dimension
            )
        )

        self.index.add(
            embeddings
        )


    def retrieve(
        self,
        query: str,
        k: int = 3,
    ) -> list[dict]:
        """
        Return the k most semantically relevant
        knowledge chunks.
        """

        if not query.strip():
            raise ValueError(
                "query cannot be empty."
            )

        query_embedding = (
            self.embedding_model.encode(
                [query],
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            .astype(np.float32)
        )

        scores, indices = (
            self.index.search(
                query_embedding,
                k,
            )
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index < 0:
                continue

            document = self.documents[
                index
            ]

            results.append({
                "id": document["id"],
                "source": document[
                    "source"
                ],
                "text": document["text"],
                "score": float(score),
            })

        return results