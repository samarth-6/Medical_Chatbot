from pathlib import Path
from pypdf import PdfReader

class DocumentLoader:
    @staticmethod
    def load_pdf(file_path: str) -> str:

        reader = PdfReader(file_path)

        pages = []

        for page in reader.pages:

            try:
                pages.append(page.extract_text())

            except Exception:
                continue

        return "\n".join(pages)

    @staticmethod
    def load_text(file_path: str) -> str:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            return f.read()

    @classmethod
    def load_document(cls, file_path: str):

        suffix = Path(file_path).suffix.lower()

        if suffix == ".pdf":
            return cls.load_pdf(file_path)

        if suffix in [".txt", ".md"]:
            return cls.load_text(file_path)

        raise ValueError(
            f"Unsupported file type: {suffix}"
        )