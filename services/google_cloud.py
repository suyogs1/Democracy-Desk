"""
Unified Google Cloud Services Manager.
Provides Vertex AI, Cloud Translation, and Cloud Logging integrations.
"""
import os
import json
import logging
from typing import Any, Dict, List, Optional

import google.cloud.logging
from google.cloud import translate_v2 as translate
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as preview_generative_models

from dotenv import load_dotenv

load_dotenv()

class GoogleCloudManager:
    """
    Manager class for all Google Cloud integrations to ensure consistent service usage.
    """
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        # Initialize Vertex AI
        if self.project_id:
            vertexai.init(project=self.project_id, location=self.location)
            self.vertex_initialized = True
        else:
            self.vertex_initialized = False
            print("Warning: GOOGLE_CLOUD_PROJECT not found. Vertex AI features might be limited.")

        # Initialize Cloud Logging
        try:
            self.logging_client = google.cloud.logging.Client(project=self.project_id)
            self.logging_client.setup_logging()
            self.logger = logging.getLogger("democracy_desk")
        except Exception:
            self.logger = logging.getLogger(__name__)

        # Initialize Translation
        try:
            self.translate_client = translate.Client()
        except Exception:
            self.translate_client = None

        # Models
        self.flash_model = GenerativeModel("gemini-1.5-flash")
        self.pro_model = GenerativeModel("gemini-1.5-pro")

    async def get_gemini_response(self, 
                                prompt: str, 
                                use_pro: bool = False, 
                                json_mode: bool = False) -> str:
        """
        Interacts with Vertex AI Gemini models.
        """
        model = self.pro_model if use_pro else self.flash_model
        
        response_schema = {"type": "OBJECT"} if json_mode else None
        
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json" if json_mode else "text/plain",
                    "temperature": 0.2 if json_mode else 0.7
                }
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Vertex AI Error: {str(e)}")
            return json.dumps({"error": str(e)}) if json_mode else f"Error: {str(e)}"

    def translate_text(self, text: str, target_language: str = "es") -> str:
        """
        Translates text using Cloud Translation API.
        """
        if not self.translate_client:
            return text
        
        try:
            result = self.translate_client.translate(text, target_language=target_language)
            return result["translatedText"]
        except Exception as e:
            self.logger.error(f"Translation Error: {str(e)}")
            return text

    def log_telemetry(self, event_name: str, payload: Dict[str, Any]):
        """
        Structured logging for telemetry.
        """
        self.logger.info(f"TELEMETRY: {event_name}", extra={"json_fields": payload})

google_cloud = GoogleCloudManager()
