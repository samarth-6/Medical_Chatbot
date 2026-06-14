import os
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

class EmbeddingModel:

    @staticmethod
    def embed_documents(texts):

        embeddings = []

        for text in texts:

            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type="retrieval_document"
            )

            embeddings.append(
                result["embedding"]
            )

        return embeddings

    @staticmethod
    def embed_query(query):

        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query,
            task_type="retrieval_query"
        )

        return result["embedding"]