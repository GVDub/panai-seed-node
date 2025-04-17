import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, model_name: str = None, timeout: int = 120):
        self.model_name = model_name or settings.DEFAULT_MODEL_NAME
        self.timeout = timeout

    async def generate_response(self, prompt: str, model_name: str = None, max_tokens: int = 512) -> str:
        chosen_model = model_name if settings.ALLOW_DYNAMIC_MODEL_SELECTION and model_name else self.model_name

        logger.debug(f"Generating response using model: {chosen_model}")
        logger.debug(f"Prompt length: {len(prompt)} characters, Max tokens: {max_tokens}")

        payload = {
            "model": chosen_model,
            "prompt": prompt,
            "num_predict": max_tokens,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(settings.OLLAMA_API_URL, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "⚠️ No response generated.")
        except Exception as e:
            logger.error(f"LLM generation error using model '{chosen_model}': {e}")
            return "❌ Error generating response from the language model."

# Optional: instantiate a global instance if needed
chat_service = ChatService()
