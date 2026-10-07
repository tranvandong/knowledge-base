from app.documents.chunks import DocumentChunk
from app.documents.models import Document


class TextChunker:
    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 100,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, document: Document) -> list[DocumentChunk]:
        text = document.content.strip()

        if not text:
            return []

        chunks: list[DocumentChunk] = []

        start = 0
        chunk_index = 0
        step = self.chunk_size - self.overlap

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            content = text[start:end].strip()

            if content:
                chunks.append(
                    DocumentChunk(
                        chunk_id=(
                            f"{document.document_id}"
                            f"_chunk_{chunk_index:03d}"
                        ),
                        document_id=document.document_id,
                        content=content,
                        chunk_index=chunk_index,
                        metadata={
                            "title": document.title,
                            "page": document.page,
                        },
                    )
                )

            start += step
            chunk_index += 1

        return chunks