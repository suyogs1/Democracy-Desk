"""
Centralized Gemini Service for model interactions.
Handles Flash and Pro models with retry logic and structured outputs.
"""
import os
import time
import json
import logging
from typing import Any, Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service wrapper for Google's Generative AI.
    """
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found in environment.")
        genai.configure(api_key=self.api_key)
        
        # Models
        self.flash_model = genai.GenerativeModel('gemini-1.5-flash')
        self.pro_model = genai.GenerativeModel('gemini-1.5-pro')

    async def get_response(self, 
                           prompt: str, 
                           use_pro: bool = False, 
                           json_mode: bool = False, 
                           retries: int = 3) -> str:
        """
        Generic text generation with retry logic.
        """
        model = self.pro_model if use_pro else self.flash_model
        
        generation_config = {}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        for attempt in range(retries):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                return response.text
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == retries - 1:
                    return f"Error: {str(e)}"
                time.sleep(2 ** attempt)

    async def get_structured_response(self, prompt: str, use_pro: bool = False) -> Dict[str, Any]:
        """
        Returns a JSON-parsed response.
        """
        raw_text = await self.get_response(prompt, use_pro=use_pro, json_mode=True)
        try:
            return json.loads(raw_text)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {raw_text}")
            return {"error": "Invalid structured response", "raw": raw_text}

gemini_service = GeminiService()
