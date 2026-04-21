import pytest
from unittest.mock import AsyncMock, patch
from core.orchestrator import Orchestrator
from core.models import ExplanationMode, UrgencyLevel, Step

@pytest.fixture
def mock_gemini():
    with patch('services.gemini_service.gemini_service.get_structured_response', new_callable=AsyncMock) as m1, \
         patch('services.gemini_service.gemini_service.get_response', new_callable=AsyncMock) as m2:
        yield m1, m2

@pytest.mark.asyncio
async def test_orchestrator_full_pipeline(mock_gemini):
    m1, m2 = mock_gemini
    
    # Mock responses for 4 agents
    m1.side_effect = [
        {"intent": "register", "category": "registration", "confidence": 0.9}, # Intent
        {"steps": [{"title": "Step 1", "description": "D1", "cta": "A1", "timeline_hint": "now"}]}, # Planner
        {"action": "Do thing", "time_estimate": "5m", "urgency": "high"} # Today
    ]
    m2.return_value = "Simplified explanation" # Explainer
    
    orchestrator = Orchestrator()
    response = await orchestrator.handle_query(
        query="How to register?", 
        state="Texas", 
        mode=ExplanationMode.SIMPLE
    )
    
    assert response.state == "Texas"
    assert len(response.steps) == 1
    assert response.today_action.urgency == UrgencyLevel.HIGH
    assert len(response.reasoning_log) == 4

@pytest.mark.asyncio
async def test_today_action_urgency_parsing(mock_gemini):
    m1, _ = mock_gemini
    m1.return_value = {"action": "Go", "time_estimate": "1min", "urgency": "medium"}
    
    from agents.today_agent import TodayActionAgent
    agent = TodayActionAgent()
    res = await agent.process("test", context={"steps": []})
    assert res.metadata["urgency"] == "medium"
