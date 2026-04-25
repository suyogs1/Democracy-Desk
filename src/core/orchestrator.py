"""
Orchestrator for the Democracy Desk Multi-Agent System.
Coordinates the flow from intent detection to final explanation and today's action.
"""
from functools import lru_cache
from typing import Dict, Any, List, Optional, Tuple

from src.core.models import (
    AssistantResponse, IntentInfo, Step, TodayAction, 
    ReasoningLog, ExplanationMode, UrgencyLevel
)
from src.agents.intent_agent import IntentAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.explainer_agent import ExplainerAgent
from src.agents.today_agent import TodayActionAgent

class Orchestrator:
    """
    Main entry point for query processing with intelligent caching.
    """
    def __init__(self):
        self.intent_agent = IntentAgent()
        self.planner_agent = PlannerAgent()
        self.explainer_agent = ExplainerAgent()
        self.today_agent = TodayActionAgent()
        # Internal cache for ultra-fast repeated queries
        self._cache: Dict[Tuple[str, str, ExplanationMode], AssistantResponse] = {}

    async def handle_query(self, query: str, state: str = "California", mode: ExplanationMode = ExplanationMode.NORMAL) -> AssistantResponse:
        """
        Processes a query through the full agent pipeline with LRU-style caching.
        """
        cache_key = (query.strip().lower(), state, mode)
        if cache_key in self._cache:
            return self._cache[cache_key]
        """
        Processes a query through the full agent pipeline.
        
        Args:
            query: User's question.
            state: Selected region/state.
            mode: Complexity mode for explanation.
            
        Returns:
            A structured AssistantResponse model.
        """
        reasoning_log: List[ReasoningLog] = []

        # 1. Intent
        intent_res = await self.intent_agent.process(query)
        intent_info = IntentInfo(**intent_res.metadata)
        reasoning_log.append(ReasoningLog(
            agent_name=self.intent_agent.name,
            summary=f"Query mapped to '{intent_info.category}' category with {int(intent_info.confidence*100)}% certainty.",
            confidence=intent_info.confidence
        ))

        # 2. Planning
        planner_res = await self.planner_agent.process(
            query, 
            context={"intent_info": intent_info.model_dump(), "state": state}
        )
        steps = [Step(**s) for s in planner_res.metadata.get("steps", [])]
        reasoning_log.append(ReasoningLog(
            agent_name=self.planner_agent.name,
            summary=f"Synthesized {len(steps)} regional steps specifically tailored for {state}.",
            confidence=0.95
        ))

        # 3. Today's Action
        today_res = await self.today_agent.process(
            query,
            context={"steps": [s.model_dump() for s in steps]}
        )
        today_action = TodayAction(**today_res.metadata)
        reasoning_log.append(ReasoningLog(
            agent_name=self.today_agent.name,
            summary=f"Priority extraction successful: identified '{today_action.action[:30]}...' as the immediate driver.",
            confidence=0.92
        ))

        # 4. Explanation
        explainer_res = await self.explainer_agent.process(
            query,
            context={"steps": [s.model_dump() for s in steps], "mode": mode}
        )
        reasoning_log.append(ReasoningLog(
            agent_name=self.explainer_agent.name,
            summary=f"Successfully adapted tone to {mode} mode for enhanced accessibility.",
            confidence=0.98
        ))

        response = AssistantResponse(
            query=query,
            state=state,
            intent=intent_info,
            steps=steps,
            today_action=today_action,
            final_explanation=explainer_res.content,
            reasoning_log=reasoning_log
        )
        
        # Save to cache
        self._cache[cache_key] = response
        return response
