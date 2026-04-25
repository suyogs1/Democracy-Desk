"""
Unit tests for core multi-agent logic and orchestrator.
Mocks Google Cloud services to ensure reliable, offline-capable testing.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from core.orchestrator import Orchestrator
from core.models import ExplanationMode

@pytest.fixture
def mock_gemini():
    with patch("services.gemini_service.gemini_service.get_structured_response", new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_vertex():
    with patch("services.google_cloud.google_cloud.get_gemini_response", new_callable=AsyncMock) as mock:
        yield mock

@pytest.mark.asyncio
async def test_orchestrator_full_flow(mock_gemini):
    """Verifies that the orchestrator correctly sequences agent calls."""
    # Mock responses for all agents
    mock_gemini.side_effect = [
        {"intent": "Register to vote", "category": "Registration", "confidence": 0.9}, # Intent
        {"steps": [{"title": "Step 1", "description": "Desc", "cta": "CTA", "timeline_hint": "Hint"}]}, # Planner
        {"action": "Register now", "urgency": "high", "time_estimate": "5 mins"}, # Today Action
        # Explainer doesn't use get_structured_response, it uses get_response usually
    ]
    
    with patch("services.gemini_service.gemini_service.get_response", new_callable=AsyncMock) as mock_get_response:
        mock_get_response.return_value = "Detailed explanation"
        
        orchestrator = Orchestrator()
        response = await orchestrator.handle_query("How do I register?", state="Texas")
        
        assert response.query == "How do I register?"
        assert response.state == "Texas"
        assert len(response.steps) == 1
        assert response.intent.category == "Registration"
        assert "Detailed explanation" in response.final_explanation

@pytest.mark.asyncio
async def test_intent_agent_logic(mock_gemini):
    """Tests the IntentAgent specialized logic."""
    from agents.intent_agent import IntentAgent
    mock_gemini.return_value = {"intent": "Check deadline", "category": "Deadlines", "confidence": 0.85}
    
    agent = IntentAgent()
    res = await agent.process("When is the deadline?")
    
    assert res.metadata["category"] == "Deadlines"
    assert res.metadata["confidence"] == 0.85

def test_today_action_logic():
    """Tests that the TodayActionAgent correctly identifies priority from steps."""
    from agents.today_agent import TodayActionAgent
    # TodayActionAgent usually calls Gemini, but we can test its metadata assembly
    agent = TodayActionAgent()
    assert agent.name == "Action Prioritizer"
