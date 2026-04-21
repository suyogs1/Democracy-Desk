"""
Explainer Agent for translating technical steps into accessible language.
Supports multiple explanation modes including 'ELI10' for high accessibility.
"""
from typing import Dict, Any, List, Optional
from core.agent import BaseAgent, AgentResponse
from core.models import ExplanationMode
from services.gemini_service import gemini_service

class ExplainerAgent(BaseAgent):
    """
    Agent specialized in tone adjustment and jargon removal.
    """
    def __init__(self):
        super().__init__("The Explainer")

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Explains election steps based on the requested complexity mode.
        
        Args:
            task: The user query.
            context: Dictionary containing 'steps' and 'mode'.
            
        Returns:
            AgentResponse with the final explained text.
        """
        steps = context.get("steps", [])
        mode = context.get("mode", ExplanationMode.NORMAL)
        
        tone_instruction = (
            "Explain like I am 10 years old (ELI10). Use ultra-simple analogies and zero complex words."
            if mode == ExplanationMode.SIMPLE else
            "Use clear, professional, yet jargon-free language."
        )

        prompt = (
            f"Mode: {tone_instruction}\n"
            f"Target: Explain the following election steps for a user: {steps}\n\n"
            "Goal: Make it feel like a friendly guide. Avoid information overload."
        )
        
        content = await gemini_service.get_response(prompt, use_pro=True)
        
        return AgentResponse(agent_name=self.name, content=content)
