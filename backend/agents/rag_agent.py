from backend.rag.vectordb import VectorDB
from backend.logger import logger
from typing import Dict, Any, List


class RAGAgent:

    def __init__(self):
        self.db = VectorDB()

    async def run(self, query: str, session_id: str, k: int = 5) -> Dict[str, Any]:
        logger.info(f"RAGAgent query: {query[:100]}... (session={session_id})")

        try:
            results = await self.db.similarity_search_async(
                session_id=session_id, query=query, k=k
            )

            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            if not documents:
                logger.info(f"No documents found for session {session_id}")
                return {"context": "", "sources": [], "has_results": False}

            contexts = []
            sources = []

            for idx, (doc, meta, distance) in enumerate(
                zip(documents, metadatas, distances)
            ):
                source = meta.get("source", "uploaded_document")
                similarity_score = 1 - (distance / 2) if distance else 0.5

                if similarity_score < 0.3:
                    logger.debug(f"Skipping low-relevance chunk: score={similarity_score:.2f}")
                    continue

                contexts.append(
                    f"[Document: {source} | Relevance: {similarity_score:.2%}]\n{doc.strip()}"
                )
                sources.append({
                    "title": source,
                    "type": "document",
                    "chunk_id": idx,
                    "relevance_score": similarity_score,
                    "content_preview": doc[:200] + "..." if len(doc) > 200 else doc,
                })

            combined_context = "\n\n---\n\n".join(contexts)
            logger.info(f"Retrieved {len(sources)} relevant chunks for query")

            return {
                "context": combined_context,
                "sources": sources,
                "has_results": len(sources) > 0,
                "total_chunks_retrieved": len(sources),
            }

        except Exception as e:
            logger.error(f"Error in RAGAgent: {e}", exc_info=True)
            return {"context": "", "sources": [], "has_results": False, "error": str(e)}
