import json
import logging
from typing import Any, Dict, Optional
from services.google_cloud import google_cloud

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service wrapper for Google's Generative AI via Vertex AI.
    """
    async def get_response(self, 
                           prompt: str, 
                           use_pro: bool = False, 
                           json_mode: bool = False, 
                           retries: int = 3) -> str:
        """
        Generic text generation via Vertex AI.
        """
        return await google_cloud.get_gemini_response(prompt, use_pro=use_pro, json_mode=json_mode)

    async def get_structured_response(self, prompt: str, use_pro: bool = False) -> Dict[str, Any]:
        """
        Returns a JSON-parsed response.
        """
        raw_text = await self.get_response(prompt, use_pro=use_pro, json_mode=True)
        try:
            # Clean up potential markdown formatting if model didn't strictly follow JSON mode
            cleaned_text = raw_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:-3].strip()
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:-3].strip()
            
            return json.loads(cleaned_text)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {raw_text}")
            return {"error": "Invalid structured response", "raw": raw_text}

gemini_service = GeminiService()
