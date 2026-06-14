from backend.db.database import get_connection
from pgvector.psycopg import register_vector
import uuid
from backend.rag.embeddings import EmbeddingModel

class VectorDB:
    @staticmethod
    def _to_pgvector(emb):
            return "[" + ",".join(str(x) for x in emb) + "]"

    def add_documents(self, session_id, chunks, source_name):
        conn = get_connection()
        register_vector(conn)
        cur = conn.cursor()
        embeddings = EmbeddingModel.embed_documents(chunks)
        for chunk, embedding in zip(chunks, embeddings):
            cur.execute(
                """
                INSERT INTO chunks (id, session_id, source, chunk_text, embedding)
                VALUES (%s, %s, %s, %s, %s::vector)
                """,
                (str(uuid.uuid4()), session_id, source_name, chunk, self._to_pgvector(embedding))
            )
        conn.commit()
        cur.close()
        conn.close()

    def similarity_search(self, session_id, query, k=5):
        conn = get_connection()
        register_vector(conn)
        cur = conn.cursor()
        query_embedding = EmbeddingModel.embed_query(query)
        query_vector = self._to_pgvector(query_embedding)
        cur.execute(
            """
            SELECT chunk_text, source, embedding <=> %s::vector as distance
            FROM chunks
            WHERE session_id = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_vector,
            session_id,
            query_vector,
            k)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {
            "documents": [[row[0] for row in rows]],
            "metadatas": [[{"source": row[1]} for row in rows]],
            "distances": [[row[2] for row in rows]]  
        }