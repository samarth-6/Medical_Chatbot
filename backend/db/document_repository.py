import uuid

from backend.db.database import (
    get_connection
)


class DocumentRepository:

    @staticmethod
    def exists(
        session_id: str,
        filename: str
    ) -> bool:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute(
            """
            SELECT 1
            FROM uploaded_documents
            WHERE session_id=%s
            AND filename=%s
            """,
            (
                session_id,
                filename
            )
        )

        exists = cur.fetchone() is not None

        cur.close()
        conn.close()

        return exists

    @staticmethod
    def create(
        session_id: str,
        filename: str,
        filepath: str
    ):

        conn = get_connection()

        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO uploaded_documents
            (
                id,
                session_id,
                filename,
                filepath
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                str(uuid.uuid4()),
                session_id,
                filename,
                filepath
            )
        )

        conn.commit()

        cur.close()
        conn.close()

    @staticmethod
    def list_documents(
        session_id: str
    ):

        conn = get_connection()

        cur = conn.cursor()

        cur.execute(
            """
            SELECT filename
            FROM uploaded_documents
            WHERE session_id=%s
            ORDER BY uploaded_at DESC
            """,
            (session_id,)
        )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [
            {
                "filename": row[0]
            }
            for row in rows
        ]

    @staticmethod
    def get_document(
        session_id: str,
        filename: str
    ):

        conn = get_connection()

        cur = conn.cursor()

        cur.execute(
            """
            SELECT filepath
            FROM uploaded_documents
            WHERE session_id=%s
            AND filename=%s
            """,
            (
                session_id,
                filename
            )
        )

        row = cur.fetchone()

        cur.close()
        conn.close()

        return row[0] if row else None

    @staticmethod
    def delete(
        session_id: str,
        filename: str
    ):

        conn = get_connection()

        cur = conn.cursor()

        cur.execute(
            """
            DELETE FROM uploaded_documents
            WHERE session_id=%s
            AND filename=%s
            """,
            (
                session_id,
                filename
            )
        )

        conn.commit()

        cur.close()
        conn.close()