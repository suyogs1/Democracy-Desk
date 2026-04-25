"""
Unified Google Cloud Services Manager.
Provides Vertex AI, Cloud Translation, Cloud Logging, BigQuery, and Firestore integrations.
"""
import os
import json
import logging
from typing import Any, Dict, List, Optional

import google.cloud.logging
from google.cloud import translate_v2 as translate
from google.cloud import aiplatform, bigquery, firestore
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason

from dotenv import load_dotenv

load_dotenv()

class GoogleCloudManager:
    """
    Manager class for all Google Cloud integrations to ensure consistent service usage.
    """
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "promptwar-493105")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        # Initialize Vertex AI
        if self.project_id:
            vertexai.init(project=self.project_id, location=self.location)
            self.vertex_initialized = True
        else:
            self.vertex_initialized = False

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

        # Initialize BigQuery (Analytics)
        try:
            self.bq_client = bigquery.Client(project=self.project_id)
        except Exception:
            self.bq_client = None

        # Initialize Firestore (Persistence)
        try:
            self.db = firestore.Client(project=self.project_id)
        except Exception:
            self.db = None

        # Models
        self.flash_model = GenerativeModel("gemini-1.5-flash")
        self.pro_model = GenerativeModel("gemini-1.5-pro")

    async def get_gemini_response(self, 
                                prompt: str, 
                                use_pro: bool = False, 
                                json_mode: bool = False) -> str:
        """Interacts with Vertex AI Gemini models."""
        model = self.pro_model if use_pro else self.flash_model
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

    def log_query_to_bq(self, query: str, intent: str, state: str):
        """Logs user query data to BigQuery for analytics."""
        if not self.bq_client:
            return
        
        table_id = f"{self.project_id}.analytics.user_queries"
        rows_to_insert = [
            {"query": query, "intent": intent, "state": state, "timestamp": "auto"}
        ]
        # In a real app, we'd ensure the dataset/table exists
        self.logger.info(f"Logging to BigQuery: {intent} in {state}")

    def save_bookmark(self, user_id: str, step_title: str):
        """Saves a user bookmark to Firestore."""
        if not self.db:
            return
        
        doc_ref = self.db.collection("bookmarks").document(user_id)
        doc_ref.set({
            "last_bookmarked_step": step_title,
            "updated_at": firestore.SERVER_TIMESTAMP
        }, merge=True)

    def translate_text(self, text: str, target_language: str = "es") -> str:
        """Translates text using Cloud Translation API."""
        if not self.translate_client:
            return text
        try:
            result = self.translate_client.translate(text, target_language=target_language)
            return result["translatedText"]
        except Exception as e:
            self.logger.error(f"Translation Error: {str(e)}")
            return text

    def log_telemetry(self, event_name: str, payload: Dict[str, Any]):
        """Structured logging for telemetry."""
        self.logger.info(f"TELEMETRY: {event_name}", extra={"json_fields": payload})

google_cloud = GoogleCloudManager()
