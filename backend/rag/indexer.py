import asyncio
from pathlib import Path

from backend.rag.document_loader import DocumentLoader
from backend.rag.chunker import TextChunker
from backend.rag.vectordb import VectorDB


class DocumentIndexer:

    def __init__(self):
        self.vectordb = VectorDB()

    async def index_file_async(self, session_id: str, file_path: str):
        """Fully async: load → chunk → embed (parallel) → bulk insert."""
        loop = asyncio.get_event_loop()

        text = await loop.run_in_executor(
            None, DocumentLoader.load_document, file_path
        )

        if not text.strip():
            return

        chunks = TextChunker.chunk_text(text)

        await self.vectordb.add_documents_async(
            session_id=session_id,
            chunks=chunks,
            source_name=Path(file_path).name,
        )

        print("=" * 50)
        print(f"File: {file_path}")
        print(f"Text Length: {len(text)}")
        print(f"Chunks Created: {len(chunks)}")
        print("=" * 50)

    def index_file(self, session_id: str, file_path: str):
        """Sync wrapper kept for compatibility."""
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.index_file_async(session_id, file_path))
        finally:
            loop.close()
