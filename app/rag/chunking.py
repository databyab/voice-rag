import uuid
from typing import List, Dict, Any
from app.config import settings
from app.utils.logging import logger

class TextChunker:
    """Configurable text chunker with overlap support."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        for doc in documents:
            content = doc.get("content", "")
            base_meta = doc.get("metadata", {})
            
            doc_chunks = self.split_text(content, base_meta)
            chunks.extend(doc_chunks)

        logger.info(f"Split {len(documents)} document pages into {len(chunks)} total chunks.")
        return chunks

    def split_text(self, text: str, base_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not text or not text.strip():
            return []

        # Split into paragraph/sentence slices
        slices = self._create_chunks(text, self.chunk_size, self.chunk_overlap)
        
        chunks = []
        source_name = base_metadata.get("source", "unknown")
        page_num = base_metadata.get("page", 1)

        for index, chunk_text in enumerate(slices):
            chunk_id = f"{source_name}_p{page_num}_c{index}_{uuid.uuid4().hex[:6]}"
            meta = {
                **base_metadata,
                "chunk_id": chunk_id,
                "chunk_index": index,
            }
            chunks.append({
                "chunk_id": chunk_id,
                "content": chunk_text,
                "metadata": meta
            })

        return chunks

    @staticmethod
    def _create_chunks(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            if end >= text_length:
                chunks.append(text[start:])
                break

            # Try to break at paragraph boundary or space
            break_pos = text.rfind("\n\n", start, end)
            if break_pos == -1 or break_pos < start + (chunk_size // 2):
                break_pos = text.rfind("\n", start, end)
            if break_pos == -1 or break_pos < start + (chunk_size // 2):
                break_pos = text.rfind(" ", start, end)

            if break_pos == -1 or break_pos <= start:
                break_pos = end

            chunks.append(text[start:break_pos].strip())
            start = max(start + 1, break_pos - chunk_overlap)

        return [c for c in chunks if c.strip()]
