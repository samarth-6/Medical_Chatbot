
from backend.rag.vectordb import VectorDB
from backend.logger import logger
from typing import Dict, Any, List, Optional


class RAGAgent:

    def __init__(self):
        self.db = VectorDB()

    async def run(
        self,
        query: str,
        session_id: str,
        k: int = 5
    ) -> Dict[str, Any]:
       
        logger.info(f"RAGAgent query: {query[:100]}... (session={session_id})")
        
        try:
            results = self.db.similarity_search(
                session_id=session_id,
                query=query,
                k=k
            )
            
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            if not documents:
                logger.info(f"No documents found for session {session_id}")
                return {
                    "context": "",
                    "sources": [],
                    "has_results": False
                }
            
            contexts = []
            sources = []
            
            for idx, (doc, meta, distance) in enumerate(zip(documents, metadatas, distances)):
                source = meta.get("source", "uploaded_document")
                chunk_id = meta.get("chunk_id", idx)
                
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
                    "chunk_id": chunk_id,
                    "relevance_score": similarity_score,
                    "content_preview": doc[:200] + "..." if len(doc) > 200 else doc
                })
            
            combined_context = "\n\n---\n\n".join(contexts)
            
            logger.info(f"Retrieved {len(sources)} relevant chunks for query")
            
            return {
                "context": combined_context,
                "sources": sources,
                "has_results": len(sources) > 0,
                "total_chunks_retrieved": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error in RAGAgent: {e}", exc_info=True)
            return {
                "context": "",
                "sources": [],
                "has_results": False,
                "error": str(e)
            }

    async def get_document_list(self, session_id: str) -> List[str]:
        try:
            collection = self.db.get_collection(session_id)
            if collection:
                results = collection.get()
                metadatas = results.get("metadatas", [])
                sources = set()
                for meta in metadatas:
                    if meta and "source" in meta:
                        sources.add(meta["source"])
                return sorted(list(sources))
            return []
        except Exception as e:
            logger.error(f"Error getting document list: {e}")
            return []