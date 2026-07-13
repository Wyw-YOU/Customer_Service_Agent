"""
Paragraph-first text chunker using tiktoken for accurate token counting.

Strategy (MVP):
 1. Split by double-newline (natural paragraph boundary).
 2. Glue paragraphs together until the token limit is reached.
 3. If a single paragraph exceeds the limit, fall back to sentence splitting.

This preserves semantic cohesion better than fixed-size sliding windows.
"""
import tiktoken


class TextChunker:
    """Split plain text into embedding-friendly chunks by paragraph boundaries."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap  # reserved for future overlap support
        # cl100k_base is the encoding used by text-embedding-3-small
        try:
            self._tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self._tokenizer = tiktoken.get_encoding("o200k_base")

    def _token_count(self, text: str) -> int:
        return len(self._tokenizer.encode(text))

    def chunk(self, text: str) -> list[str]:
        """Split text into chunks respecting paragraph boundaries."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: list[str] = []
        current = ""

        for para in paragraphs:
            candidate = current + ("\n\n" if current else "") + para
            if self._token_count(candidate) <= self._chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                # A single paragraph that's too long → sentence-level split
                if self._token_count(para) > self._chunk_size:
                    chunks.extend(self._split_long_paragraph(para))
                    current = ""
                else:
                    current = para

        if current:
            chunks.append(current)
        return chunks

    def _split_long_paragraph(self, text: str) -> list[str]:
        """Fallback: split an oversized paragraph by sentence delimiters."""
        sentences = (
            text.replace("。", "。\n")
            .replace("！", "！\n")
            .replace("？", "？\n")
            .split("\n")
        )
        chunks: list[str] = []
        current = ""
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            if self._token_count(current + sent) <= self._chunk_size:
                current += sent
            else:
                if current:
                    chunks.append(current)
                current = sent
        if current:
            chunks.append(current)
        return chunks
