"""
Planner Agent for generating election process timelines.
Adapts steps based on user regional context and specific intent.
"""
from typing import Dict, Any, List, Optional
from src.core.agent import BaseAgent, AgentResponse
from src.core.models import Step
from src.services.google_cloud import google_cloud

class PlannerAgent(BaseAgent):
    """
    Agent specialized in creating actionable, step-by-step election guides.
    """
    def __init__(self):
        super().__init__("Process Planner")

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Generates a series of steps adjusted for the specific state and query.
        
        Args:
            task: The user's query.
            context: Dictionary containing 'intent_info' and 'state'.
            
        Returns:
            AgentResponse with a list of Step models in metadata.
        """
        intent_info = context.get("intent_info", {})
        state = context.get("state", "California") # Default state
        
        prompt = (
            "You are an Election Process Planner. Create an interactive timeline for the user's intent. "
            f"State Context: {state}\n"
            f"Intent: {intent_info.get('intent', task)}\n\n"
            "Requirements:\n"
            "1. Generate ordered steps that match this JSON structure: "
            "{'steps': [{'title': string, 'description': string, 'cta': string, 'timeline_hint': string}]}\n"
            "2. Ensure the steps are specific to the the selected state where possible (using your knowledge).\n"
            "3. Make descriptions detailed but actionable."
        )
        
        result_str = await google_cloud.get_gemini_response(prompt, json_mode=True)
        import json
        result = json.loads(result_str)
        raw_steps = result.get("steps", [])
        
        # Hydrate Step models
        steps = [Step(**s) for s in raw_steps]
        
        return AgentResponse(
            agent_name=self.name,
            content=f"Generated {len(steps)} steps for {state}.",
            metadata={"steps": [s.model_dump() for s in steps]}
        )
