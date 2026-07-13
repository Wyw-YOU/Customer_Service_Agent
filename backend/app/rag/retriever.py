"""
Retriever: combines embedding and vector search into a single call.
Usage:
    retriever = Retriever()
    context, sources = await retriever.format_context("退换货政策是什么")
"""
from app.rag.embedding import EmbeddingClient
from app.rag.vectorstore import VectorStore


class Retriever:
    """Embeds a query, searches Qdrant, and formats results as prompt context."""

    def __init__(self) -> None:
        self._embedding = EmbeddingClient()
        self._vectorstore = VectorStore()

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Embed the query and return top-k chunks with metadata from Qdrant."""
        query_vector = await self._embedding.embed_single(query)
        results = self._vectorstore.search(query_vector, top_k=top_k)
        return results

    async def format_context(self, query: str, top_k: int = 5) -> tuple[str, list[str]]:
        """Retrieve and format chunks ready for prompt injection.

        Returns:
            context (str):  formatted context block for the LLM prompt
            sources (list[str]):  deduplicated list of document names used
        """
        results = await self.retrieve(query, top_k=top_k)
        if not results:
            return "", []

        parts: list[str] = []
        sources: list[str] = []
        for r in results:
            doc_name = r.get("document_name", "unknown")
            content = r.get("content", "")
            parts.append(f"[来源: {doc_name}]\n{content}")
            if doc_name not in sources:
                sources.append(doc_name)

        context = "\n\n---\n\n".join(parts)
        return context, sources
