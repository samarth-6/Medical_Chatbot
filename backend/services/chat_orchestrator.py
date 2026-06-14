from typing import Any, Dict, Optional

from backend.agents.planner_agent import (
    PlannerAgent
)
from backend.agents.rag_agent import (
    RAGAgent
)
from backend.agents.synthesis_agent import (
    SynthesisAgent
)
from backend.agents.web_search_agent import (
    WebSearchAgent
)
from backend.logger import logger


class ChatOrchestrator:

    def __init__(self):

        self.planner = PlannerAgent()

        self.web_agent = WebSearchAgent()

        self.rag_agent = RAGAgent()

        self.synthesizer = (
            SynthesisAgent()
        )

    async def chat(
        self,
        query: str,
        mode: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:

        logger.info(
            f"Chat request | mode={mode} | query={query[:100]}"
        )

        plan = await self.planner.plan(
            query=query,
            mode=mode
        )

        if not plan["allowed"]:

            logger.info(
                f"Blocked query: {plan['reason']}"
            )

            return {
                "answer": plan["reason"],
                "sources": []
            }

        worker = plan["worker"]

        if worker == "rag":

            if not session_id:

                return {
                    "answer":
                    "No active document session found. "
                    "Please upload documents first.",
                    "sources": []
                }

            try:

                result = await self.rag_agent.run(
                    query=query,
                    session_id=session_id
                )

            except Exception as e:

                logger.exception(e)

                result = {
                    "context": "",
                    "sources": []
                }

        else:

            try:

                result = await self.web_agent.run(
                    query=query
                )

            except Exception as e:

                logger.exception(e)

                result = {
                    "context": "",
                    "sources": []
                }

        context = result.get(
            "context",
            ""
        )

        sources = result.get(
            "sources",
            []
        )

        if context.strip():

            try:

                answer = (
                    await self.synthesizer.answer_from_context(
                        query=query,
                        context=context
                    )
                )

                return {
    "answer": answer,
    "sources": [] if worker == "rag" else sources
}

            except Exception as e:

                logger.exception(e)

        if worker == "rag":

            return {
                "answer":
                "No relevant information was found in the uploaded documents.",
                "sources": []
            }

        try:

            answer = (
                await self.synthesizer.answer_from_knowledge(
                    query=query
                )
            )

        except Exception as e:

            logger.exception(e)

            answer = (
                "Unable to generate a response at this time."
            )

        return {
            "answer":
            "⚠️ Trusted medical websites did not return sufficient information.\n\n"
            "The following answer is based on Gemini's general medical knowledge.\n\n"
            f"{answer}",
            "sources": [
                {
                    "title": "Gemini General Medical Knowledge",
                    "url": None,
                    "type": "llm"
                }
            ]
        }