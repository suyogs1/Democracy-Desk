"""
Today Action Engine for driving immediate user participation.
Selected one high-impact action from the current context.
"""
from typing import Dict, Any, Optional
from core.agent import BaseAgent, AgentResponse
from core.models import TodayAction, UrgencyLevel
from services.gemini_service import gemini_service

class TodayActionAgent(BaseAgent):
    """
    Agent specialized in identifying the single most important next step for a user.
    """
    def __init__(self):
        super().__init__("Momentum Engine")

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Extracts a single 'Today Action' from the planned steps.
        
        Args:
            task: The user query.
            context: Dictionary containing 'steps'.
            
        Returns:
            AgentResponse with TodayAction in metadata.
        """
        steps = context.get("steps", [])
        
        prompt = (
            "Analyze the following planned election steps and pick the SINGLE most important "
            "action the user should take TODAY to maintain momentum.\n\n"
            f"Steps: {steps}\n\n"
            "Return a JSON object: "
            "{'action': string, 'time_estimate': string, 'urgency': 'low'|'medium'|'high'}"
        )
        
        result = await gemini_service.get_structured_response(prompt, use_pro=False)
        action_data = TodayAction(**result)
        
        return AgentResponse(
            agent_name=self.name,
            content=action_data.action,
            metadata=action_data.model_dump()
        )
