"""
Knowledge service: orchestrates the full upload pipeline.
  PostgreSQL save → chunk → embed → Qdrant upsert → mark INDEXED
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.rag.chunker import TextChunker
from app.rag.embedding import EmbeddingClient
from app.rag.vectorstore import VectorStore
from app.schemas.knowledge import KnowledgeUploadRequest, KnowledgeStatusResponse
from app.utils.logger import logger


class KnowledgeService:
    """Orchestrates document ingestion into both PostgreSQL and Qdrant."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._chunker = TextChunker()
        self._embedding = EmbeddingClient()
        self._vectorstore = VectorStore()

    async def upload(self, request: KnowledgeUploadRequest) -> KnowledgeStatusResponse:
        """Run the full ingestion pipeline for a knowledge document."""
        # 1. Save document record to PostgreSQL
        doc = KnowledgeDocument(
            name=request.name,
            type=request.type,
            version="v1.0",
            status="PENDING",
        )
        self._session.add(doc)
        await self._session.flush()

        # 2. Chunk the raw content
        chunk_texts = self._chunker.chunk(request.content)

        # 3. Save chunks to PostgreSQL
        for i, text in enumerate(chunk_texts):
            chunk = KnowledgeChunk(
                document_id=doc.id,
                chunk_id=f"{doc.id}_chunk_{i}",
                content=text,
                meta={"source": request.name, "type": request.type},
            )
            self._session.add(chunk)
        await self._session.flush()
        await self._session.commit()

        try:
            # 4. Batch-embed all chunks
            vectors = await self._embedding.embed(chunk_texts)

            # 5. Build and upsert Qdrant points
            self._vectorstore.ensure_collection()
            points = []
            for i, (text, vector) in enumerate(zip(chunk_texts, vectors)):
                points.append({
                    "id": f"{doc.id}_chunk_{i}",
                    "vector": vector,
                    "payload": {
                        "chunk_id": f"{doc.id}_chunk_{i}",
                        "content": text,
                        "document_id": doc.id,
                        "document_name": request.name,
                        "doc_type": request.type,
                    },
                })
            self._vectorstore.upsert(points)

            # 6. Mark as successfully indexed
            doc.status = "INDEXED"
            await self._session.commit()

        except Exception:
            logger.exception("Failed to index document %d into Qdrant", doc.id)
            doc.status = "ERROR"
            await self._session.commit()

        return KnowledgeStatusResponse(
            id=doc.id,
            name=doc.name,
            type=doc.type,
            status=doc.status,
            chunk_count=len(chunk_texts),
            created_at=doc.created_at,
        )

    async def get_status(self, doc_id: int) -> KnowledgeStatusResponse | None:
        """Return the indexing status for a document by ID."""
        doc = await self._session.get(KnowledgeDocument, doc_id)
        if doc is None:
            return None

        count_result = await self._session.execute(
            select(func.count(KnowledgeChunk.id)).where(KnowledgeChunk.document_id == doc_id)
        )
        chunk_count = count_result.scalar_one()

        return KnowledgeStatusResponse(
            id=doc.id,
            name=doc.name,
            type=doc.type,
            status=doc.status,
            chunk_count=chunk_count,
            created_at=doc.created_at,
        )
