"""
Local embedding client using sentence-transformers.
DeepSeek API does not provide an embeddings endpoint, so we use a local
all-MiniLM-L6-v2 model (384-dimensional) for MVP. The model is downloaded
once on first use and cached locally.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.config.settings import settings

# Shared thread pool for running sync SentenceTransformer.encode in background
_embedding_executor = ThreadPoolExecutor(max_workers=2)


class EmbeddingClient:
    """Local embedding via sentence-transformers (all-MiniLM-L6-v2, 384-dim).

    SentenceTransformer is synchronous, so we offload work to a thread pool
    to avoid blocking the async event loop.
    """

    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        model_name = settings.embedding_model
        self._model = SentenceTransformer(model_name)
        self._dim = self._model.get_sentence_embedding_dimension()

    @property
    def dimension(self) -> int:
        """Return the output vector dimension."""
        return self._dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Batch-embed multiple texts."""
        loop = asyncio.get_running_loop()
        embeddings = await loop.run_in_executor(
            _embedding_executor,
            self._model.encode,
            texts,
        )
        return [e.tolist() for e in embeddings]

    async def embed_single(self, text: str) -> list[float]:
        """Convenience: embed a single text string."""
        results = await self.embed([text])
        return results[0]
