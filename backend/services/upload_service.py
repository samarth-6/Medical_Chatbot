import os
from pathlib import Path

from backend.config import (
    UPLOAD_DIR
)


class UploadService:

    @staticmethod
    async def save_file(
        uploaded_file,
        session_id
    ):

        session_folder = os.path.join(
            UPLOAD_DIR,
            session_id
        )

        os.makedirs(
            session_folder,
            exist_ok=True
        )

        destination = os.path.join(
            session_folder,
            uploaded_file.filename
        )

        content = await uploaded_file.read()

        with open(
            destination,
            "wb"
        ) as f:

            f.write(content)

        return destination