import uuid
import asyncio
from contextlib import contextmanager

from pgvector.psycopg import register_vector

from backend.db.database import get_pool
from backend.rag.embeddings import EmbeddingModel


@contextmanager
def _conn():
    pool = get_pool()
    conn = pool.getconn()
    register_vector(conn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


class VectorDB:

    @staticmethod
    def _to_pgvector(emb) -> str:
        return "[" + ",".join(str(x) for x in emb) + "]"

    async def add_documents_async(
        self, session_id: str, chunks: list[str], source_name: str
    ):
        """Embed all chunks in parallel, then bulk-insert with executemany."""
        if not chunks:
            return

        embeddings = await EmbeddingModel.embed_documents_async(chunks)

        rows = [
            (str(uuid.uuid4()), session_id, source_name, chunk,
             self._to_pgvector(emb))
            for chunk, emb in zip(chunks, embeddings)
        ]

        with _conn() as conn:
            cur = conn.cursor()
            cur.executemany(
                """
                INSERT INTO chunks (id, session_id, source, chunk_text, embedding)
                VALUES (%s, %s, %s, %s, %s::vector)
                """,
                rows,
            )

    def add_documents(self, session_id: str, chunks: list[str], source_name: str):
        """Sync wrapper (used by the old sync indexer path)."""
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(
                self.add_documents_async(session_id, chunks, source_name)
            )
        finally:
            loop.close()

    async def similarity_search_async(
        self, session_id: str, query: str, k: int = 5
    ) -> dict:
        query_embedding = await EmbeddingModel.embed_query_async(query)
        query_vector = self._to_pgvector(query_embedding)

        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT chunk_text, source, embedding <=> %s::vector AS distance
                FROM chunks
                WHERE session_id = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (query_vector, session_id, query_vector, k),
            )
            rows = cur.fetchall()

        return {
            "documents": [[r[0] for r in rows]],
            "metadatas": [[{"source": r[1]} for r in rows]],
            "distances": [[r[2] for r in rows]],
        }

    def similarity_search(self, session_id: str, query: str, k: int = 5) -> dict:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.similarity_search_async(session_id, query, k)
            )
        finally:
            loop.close()
