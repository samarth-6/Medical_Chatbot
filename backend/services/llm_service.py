import google.generativeai as genai
from backend.config import GEMINI_API_KEY, GEMINI_MODEL
import logging

logger = logging.getLogger(__name__)

model_name = GEMINI_MODEL


class LLMService:
    _model = None
    _model_name = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            genai.configure(api_key=GEMINI_API_KEY)
            
            model_name = "models/gemini-2.5-flash"  
            
            try:
                logger.info(f"Initializing model: {model_name}")
                cls._model = genai.GenerativeModel(model_name)
                cls._model_name = model_name
                logger.info(f"✅ LLM Service initialized with model: {model_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize {model_name}: {e}")
                raise Exception(f"No available Gemini models found: {e}")
        
        return cls._model

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate a response from the LLM"""
        try:
            model = self.get_model()
            
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
            
            if response and hasattr(response, 'text') and response.text:
                return response.text
            else:
                logger.error("Empty or invalid response from model")
                return "I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"
    
    async def generate_with_context(self, query: str, context: str) -> str:
        """Generate a response using retrieved context (RAG pattern)"""
        prompt = f"""Based on the following context, please answer the user's question.

Context:
{context}

User Question: {query}

Please provide a helpful, accurate answer based on the context above. If the context doesn't contain relevant information, say so honestly."""

        return await self.generate(prompt)


llm_service = LLMService()

async def generate_response(prompt: str) -> str:
    """Convenience function for generating responses"""
    return await llm_service.generate(prompt)