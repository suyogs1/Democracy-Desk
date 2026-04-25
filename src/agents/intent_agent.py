"""
Intent Detection Agent for parsing user queries.
Uses Gemini Flash to categorize and validate user requests.
"""
from typing import Dict, Any, Optional
from src.core.agent import BaseAgent, AgentResponse
from src.core.models import IntentInfo
from src.services.google_cloud import google_cloud

class IntentAgent(BaseAgent):
    """
    Agent specialized in identifying the user's election-related intent.
    """
    def __init__(self):
        super().__init__("Intent Detector")

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Detects user intent and returns a structured classification.
        
        Args:
            task: The user's query.
            context: Not used.
            
        Returns:
            AgentResponse with IntentInfo in metadata.
        """
        prompt = (
            "You are an Intent Detection Agent for an election assistant. "
            "Analyze the user query and return a JSON object that matches the following structure: "
            "{'intent': string, 'category': string, 'confidence': float}\n\n"
            f"User Query: {task}"
        )
        
        result = await gemini_service.get_structured_response(prompt, use_pro=False)
        # Validation via Pydantic
        intent_info = IntentInfo(**result)
        
        return AgentResponse(
            agent_name=self.name,
            content=intent_info.intent,
            metadata=intent_info.model_dump()
        )
