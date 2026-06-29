import uuid
from contextlib import contextmanager
from backend.db.database import get_pool


@contextmanager
def _conn():
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


class DocumentRepository:

    @staticmethod
    def exists(session_id: str, filename: str) -> bool:
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM uploaded_documents WHERE session_id=%s AND filename=%s",
                (session_id, filename),
            )
            return cur.fetchone() is not None

    @staticmethod
    def create(session_id: str, filename: str, filepath: str):
        with _conn() as conn:
            conn.cursor().execute(
                """
                INSERT INTO uploaded_documents (id, session_id, filename, filepath)
                VALUES (%s, %s, %s, %s)
                """,
                (str(uuid.uuid4()), session_id, filename, filepath),
            )

    @staticmethod
    def list_documents(session_id: str):
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT filename FROM uploaded_documents WHERE session_id=%s ORDER BY uploaded_at DESC",
                (session_id,),
            )
            return [{"filename": row[0]} for row in cur.fetchall()]

    @staticmethod
    def get_document(session_id: str, filename: str):
        with _conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT filepath FROM uploaded_documents WHERE session_id=%s AND filename=%s",
                (session_id, filename),
            )
            row = cur.fetchone()
            return row[0] if row else None

    @staticmethod
    def delete(session_id: str, filename: str):
        with _conn() as conn:
            conn.cursor().execute(
                "DELETE FROM uploaded_documents WHERE session_id=%s AND filename=%s",
                (session_id, filename),
            )

    @staticmethod
    def delete_chunks(session_id: str, filename: str):
        """Delete vector chunks for a document in the same pool connection."""
        with _conn() as conn:
            conn.cursor().execute(
                "DELETE FROM chunks WHERE session_id=%s AND source=%s",
                (session_id, filename),
            )
