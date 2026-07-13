"""
Qdrant vector database client wrapper.
Provides CRUD operations and vector search on the knowledge_chunks collection.

Note: Uses the synchronous qdrant_client API because its async support is
incomplete. HTTP round-trips are fast enough for MVP; wrap with
asyncio.to_thread if it becomes a bottleneck in production.
"""
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config.settings import settings

# all-MiniLM-L6-v2 produces 384-dimensional vectors.
# When switching embedding models, update this and re-create the Qdrant collection.
VECTOR_SIZE = 384


class VectorStore:
    """Qdrant wrapper for the knowledge_chunks collection."""

    COLLECTION_NAME = "knowledge_chunks"

    def __init__(self) -> None:
        self._client = QdrantClient(url=settings.qdrant_url)

    def ensure_collection(self) -> None:
        """Create the collection if it doesn't exist (idempotent)."""
        names = [c.name for c in self._client.get_collections().collections]
        if self.COLLECTION_NAME not in names:
            self._client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=qmodels.VectorParams(
                    size=VECTOR_SIZE,
                    distance=qmodels.Distance.COSINE,
                ),
            )

    def upsert(self, points: list[dict]) -> None:
        """Insert or update points in Qdrant.

        Each point dict:
            id: str          — chunk_id (converted to UUID internally)
            vector: list[float]
            payload: dict    — {chunk_id, content, document_id, document_name, doc_type}
        """
        qpoints = [
            qmodels.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, p["id"])),
                vector=p["vector"],
                payload=p["payload"],
            )
            for p in points
        ]
        self._client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=qpoints,
        )

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        """Return top-k results as list of {id, score, ...payload}."""
        results = self._client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
        )
        return [
            {"id": r.id, "score": r.score, **r.payload}
            for r in results.points
        ]

    def delete_by_document(self, document_id: int) -> None:
        """Delete all chunks for a given document_id."""
        self._client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )
