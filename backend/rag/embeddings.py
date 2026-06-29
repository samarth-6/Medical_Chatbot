import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_executor = ThreadPoolExecutor(max_workers=8)


def _embed_single(text: str, task_type: str) -> list:
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type=task_type,
    )
    return result["embedding"]


class EmbeddingModel:

    @staticmethod
    async def embed_documents_async(texts: list[str]) -> list[list]:
        """Embed all chunks concurrently using the thread pool."""
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(_executor, _embed_single, text, "retrieval_document")
            for text in texts
        ]
        return await asyncio.gather(*tasks)

    @staticmethod
    def embed_documents(texts: list[str]) -> list[list]:
        """Sync wrapper kept for callers that can't easily go async."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                EmbeddingModel.embed_documents_async(texts)
            )
        finally:
            loop.close()

    @staticmethod
    def embed_query(query: str) -> list:
        return _embed_single(query, "retrieval_query")

    @staticmethod
    async def embed_query_async(query: str) -> list:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor, _embed_single, query, "retrieval_query"
        )
