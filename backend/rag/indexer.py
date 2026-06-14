from pathlib import Path

from backend.rag.document_loader import (
    DocumentLoader
)
from backend.rag.chunker import (
    TextChunker
)
from backend.rag.vectordb import (
    VectorDB
)
class DocumentIndexer:

    def __init__(self):

        self.vectordb = VectorDB()

    def index_file(
        self,
        session_id: str,
        file_path: str
    ):

        text = (
            DocumentLoader.load_document(
                file_path
            )
        )

        if not text.strip():
            return

        chunks = (
            TextChunker.chunk_text(
                text
            )
        )

        self.vectordb.add_documents(
            session_id=session_id,
            chunks=chunks,
            source_name=Path(
                file_path
            ).name
        )

        print("=" * 50)
        print(f"File: {file_path}")
        print(f"Text Length: {len(text)}")
        print(f"Chunks Created: {len(chunks)}")
        print("=" * 50)