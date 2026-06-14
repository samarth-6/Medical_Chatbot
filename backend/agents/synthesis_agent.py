from backend.services.llm_service import (
    LLMService
)


class SynthesisAgent:

    def __init__(self):

        self.llm = LLMService()

    async def answer_from_context(
        self,
        query: str,
        context: str
    ):

        prompt = f"""
You are a medical information assistant.

Rules:

1. Answer ONLY from the provided context.

2. If information is missing,
say "I could not find enough information."

3. Never invent facts.

4. Never provide diagnosis.

5. Never prescribe medication.

Question:
{query}

Context:
{context}
"""

        return await self.llm.generate(
            prompt
        )

    async def answer_from_knowledge(
        self,
        query: str
    ):

        prompt = f"""
You are a medical information assistant.

Answer the question using your medical knowledge.

Rules:

1. Do not diagnose.
2. Do not prescribe medication.
3. Mention that the information
   should not replace professional
   medical advice.
4. Keep the answer concise.

Question:
{query}
"""

        return await self.llm.generate(
            prompt
        )