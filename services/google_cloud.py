"""
Unified Google Cloud Services Manager.
Provides Vertex AI, Translation, Logging, BigQuery, Firestore, and Text-to-Speech integrations.
"""
import os
import json
import base64
import logging
from typing import Any, Dict, List, Optional

import google.cloud.logging
from google.cloud import translate_v2 as translate
from google.cloud import aiplatform, bigquery, firestore, texttospeech
import vertexai
from vertexai.generative_models import GenerativeModel

from dotenv import load_dotenv

load_dotenv()

class GoogleCloudManager:
    """
    Manager class for all Google Cloud integrations.
    """
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "promptwar-493105")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.api_key = os.getenv("VERTEX_AI_API_KEY")
        
        # Initialize Vertex AI
        if self.project_id:
            try:
                vertexai.init(project=self.project_id, location=self.location)
                self.vertex_initialized = True
            except Exception:
                self.vertex_initialized = False
        else:
            self.vertex_initialized = False

        # Initialize Services lazily to save memory
        self._logging_client = None
        self._translate_client = None
        self._bq_client = None
        self._db = None
        self._tts_client = None
        
        # Models
        self.flash_model = GenerativeModel("gemini-1.5-flash")
        self.pro_model = GenerativeModel("gemini-1.5-pro")

        # Fallback Logger
        self.logger = logging.getLogger("democracy_desk")

    @property
    def tts_client(self):
        if not self._tts_client:
            try:
                self._tts_client = texttospeech.TextToSpeechClient()
            except Exception:
                self._tts_client = None
        return self._tts_client

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

    def text_to_speech_base64(self, text: str) -> Optional[str]:
        """Converts text to speech and returns a base64 encoded audio string."""
        if not self.tts_client:
            return None
        
        try:
            input_text = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            response = self.tts_client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )
            return base64.b64encode(response.audio_content).decode("utf-8")
        except Exception as e:
            self.logger.error(f"TTS Error: {str(e)}")
            return None

    def log_telemetry(self, event_name: str, payload: Dict[str, Any]):
        """Structured logging for telemetry."""
        self.logger.info(f"TELEMETRY: {event_name}", extra={"json_fields": payload})

google_cloud = GoogleCloudManager()
