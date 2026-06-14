import logging
import re
from typing import Tuple

import google.generativeai as genai

from backend.config import GEMINI_API_KEY
from backend.services.medical_keywords import MEDICAL_KEYWORDS,BODY_PARTS,SYMPTOMS,COMMON_MEDICAL_PATTERNS

logger = logging.getLogger(__name__)


class MedicalGuardrail:

    HIGH_RISK_KEYWORDS = {
        "abuse",
        "misuse",
        "recreational",
        "get high",
        "overdose",
        "crush",
        "snort",
        "inject",
        "smoke",
        "chew",
        "self-medicate",
    }

    DANGEROUS_PATTERNS = [
        r"should i (take|eat|use|consume) (\w+)",
        r"can i (take|eat|use|consume) (\w+)",
        r"is it safe to (take|eat|use|consume) (\w+)",
        r"how to (abuse|misuse) (\w+)",
        r"get high on (\w+)",
        r"recreational use of (\w+)",
    ]

    SENSITIVE_DRUGS = {
        "fentanyl",
        "heroin",
        "cocaine",
        "methamphetamine",
        "oxycodone",
        "xanax",
        "valium",
        "morphine",
        "codeine",
        "tramadol",
        "adderall",
        "ritalin",
        "ketamine",
        "mdma",
        "ecstasy",
    }

    ABUSE_INDICATORS = {
        "get high",
        "recreational",
        "abuse",
        "misuse",
        "without prescription",
        "illegal",
        "street",
    }

    

    def __init__(self):

        self.llm_available = False

        try:

            genai.configure(
                api_key=GEMINI_API_KEY
            )

            self.model = genai.GenerativeModel(
                "gemini-2.0-flash-exp"
            )

            self.llm_available = True

            logger.info(
                "MedicalGuardrail initialized"
            )

        except Exception as e:

            logger.warning(
                f"Gemini unavailable: {e}"
            )

    @classmethod
    def _contains_medical_keywords(
        cls,
        query: str
    ) -> bool:
    
        query_lower = query.lower()

        for pattern in COMMON_MEDICAL_PATTERNS:

            if re.search(
                pattern,
                query.lower()
            ):

                return (
                    True
                )
    
        for keyword in MEDICAL_KEYWORDS:
            if keyword in query_lower:
                return True
    
        for body_part in BODY_PARTS:
            if body_part in query_lower:
                return True
    
        for symptom in SYMPTOMS:
            if symptom in query_lower:
                return True
    
        return False

    @classmethod
    def _is_dangerous_query(
        cls,
        query: str
    ) -> Tuple[bool, str]:

        query_lower = query.lower()

        for keyword in cls.HIGH_RISK_KEYWORDS:

            if keyword in query_lower:

                return (
                    True,
                    "drug misuse intent detected"
                )

        for pattern in cls.DANGEROUS_PATTERNS:

            if re.search(
                pattern,
                query_lower
            ):

                return (
                    True,
                    "unsafe medication usage request"
                )

        for drug in cls.SENSITIVE_DRUGS:

            if drug in query_lower:

                for indicator in cls.ABUSE_INDICATORS:

                    if indicator in query_lower:

                        return (
                            True,
                            "controlled substance misuse"
                        )

        return (
            False,
            ""
        )

    async def _llm_domain_check(
        self,
        query: str
    ) -> bool:

        if not self.llm_available:

            return False

        prompt = f"""
Determine whether the following query
is genuinely related to medicine,
healthcare, diseases, symptoms,
treatments, medications,
clinical research, or health.

Query:
{query}

Answer ONLY:

YES
or
NO
"""

        try:

            response = self.model.generate_content(
                prompt
            )

            answer = (
                response.text
                .strip()
                .upper()
            )

            return answer.startswith(
                "YES"
            )

        except Exception as e:

            logger.error(
                f"Guardrail LLM check failed: {e}"
            )

            return False

    async def is_medical_query(
        self,
        query: str
    ) -> Tuple[bool, str]:

        if not query.strip():

            return (
                False,
                "Please enter a medical or healthcare-related question."
            )

        dangerous, _ = (
            self._is_dangerous_query(
                query
            )
        )

        if dangerous:

            return (
                False,
                "I can help with legitimate medical and health-related questions, "
                "but I cannot provide instructions for drug misuse, unsafe medication use, "
                "or potentially harmful activities."
            )

        query_lower = query.lower()

        for drug in self.SENSITIVE_DRUGS:

            if drug in query_lower:

                if any(
                    phrase in query_lower
                    for phrase in [
                        "prescribed",
                        "prescription",
                        "medication",
                        "medicine",
                        "treatment",
                    ]
                ):

                    return (
                        True,
                        f"medical query about {drug}"
                    )

                return (
                    False,
                    f"I cannot provide guidance on using {drug} outside legitimate "
                    f"medical contexts. Please consult a licensed healthcare professional."
                )

        if self._contains_medical_keywords(
            query
        ):

            return (
                True,
                "medical keyword match"
            )

        llm_medical = (
            await self._llm_domain_check(
                query
            )
        )

        if llm_medical:

            return (
                True,
                "medical query detected by Gemini"
            )

        return (
            False,
            "I specialize in medical and healthcare topics. "
            "Please ask a question related to symptoms, diseases, medications, "
            "treatments, medical research, or general health."
        )