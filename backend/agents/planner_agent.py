from backend.services.guardrails import MedicalGuardrail
from backend.logger import logger


class PlannerAgent:

    def __init__(self):
        self.guardrail = MedicalGuardrail()

    async def plan(self, query: str, mode: str) -> dict:
        is_allowed, reason = await self.guardrail.is_medical_query(query)
        
        if not is_allowed:
            logger.warning(f"Query blocked: {query[:100]} - {reason}")
            return {
                "allowed": False,
                "reason": reason
            }
        
        if mode == "rag":
            return {"allowed": True, "worker": "rag"}
        
        return {"allowed": True, "worker": "web"}