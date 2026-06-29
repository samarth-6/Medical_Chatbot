from typing import Any, Dict, Optional

from backend.agents.planner_agent import PlannerAgent
from backend.agents.rag_agent import RAGAgent
from backend.agents.synthesis_agent import SynthesisAgent
from backend.agents.web_search_agent import WebSearchAgent
from backend.db.document_repository import DocumentRepository
from backend.logger import logger


class ChatOrchestrator:

    def __init__(self):
        self.planner = PlannerAgent()
        self.web_agent = WebSearchAgent()
        self.rag_agent = RAGAgent()
        self.synthesizer = SynthesisAgent()

    async def chat(
        self,
        query: str,
        mode: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        logger.info(f"Chat request | mode={mode} | query={query[:100]}")

        plan = await self.planner.plan(query=query, mode=mode)

        if not plan["allowed"]:
            logger.info(f"Blocked query: {plan['reason']}")
            return {"answer": plan["reason"], "sources": []}

        worker = plan["worker"]

        # ── 1. RAG retrieval (always attempted when session has documents) ──
        rag_context = ""
        rag_sources: list = []

        if session_id:
            # Check whether this session actually has any indexed documents
            session_docs = DocumentRepository.list_documents(session_id)
            if session_docs:
                try:
                    rag_result = await self.rag_agent.run(
                        query=query, session_id=session_id
                    )
                    rag_context = rag_result.get("context", "")
                    rag_sources = rag_result.get("sources", [])
                    if rag_context:
                        logger.info(
                            f"RAG returned {len(rag_sources)} chunks for session {session_id}"
                        )
                except Exception as e:
                    logger.exception(f"RAG retrieval failed: {e}")

        # ── 2. Web retrieval (skipped only when mode == 'rag' AND rag found results) ──
        web_context = ""
        web_sources: list = []

        run_web = worker == "web" or (worker == "rag" and not rag_context)

        if run_web:
            try:
                web_result = await self.web_agent.run(query=query)
                web_context = web_result.get("context", "")
                web_sources = web_result.get("sources", [])
            except Exception as e:
                logger.exception(f"Web search failed: {e}")

        # ── 3. Merge contexts ──────────────────────────────────────────────
        context_parts = []
        if rag_context:
            context_parts.append(
                "=== CONTEXT FROM UPLOADED DOCUMENTS ===\n\n" + rag_context
            )
        if web_context:
            context_parts.append(
                "=== CONTEXT FROM TRUSTED MEDICAL WEBSITES ===\n\n" + web_context
            )

        combined_context = "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(context_parts)
        all_sources = rag_sources + web_sources

        # ── 4. Synthesise ──────────────────────────────────────────────────
        if combined_context.strip():
            try:
                answer = await self.synthesizer.answer_from_context(
                    query=query, context=combined_context
                )
                return {"answer": answer, "sources": all_sources}
            except Exception as e:
                logger.exception(f"Synthesis from context failed: {e}")

        # ── 5. Fallback: pure LLM knowledge ───────────────────────────────
        if worker == "rag":
            return {
                "answer": (
                    "No relevant information was found in the uploaded documents."
                ),
                "sources": [],
            }

        try:
            answer = await self.synthesizer.answer_from_knowledge(query=query)
        except Exception as e:
            logger.exception(e)
            answer = "Unable to generate a response at this time."

        return {
            "answer": (
                "⚠️ Trusted medical websites did not return sufficient information.\n\n"
                "The following answer is based on Gemini's general medical knowledge.\n\n"
                f"{answer}"
            ),
            "sources": [
                {"title": "Gemini General Medical Knowledge", "url": None, "type": "llm"}
            ],
        }