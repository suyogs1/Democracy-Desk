import pytest
from unittest.mock import AsyncMock, patch
from src.core.orchestrator import Orchestrator
from src.core.models import ExplanationMode, UrgencyLevel

@pytest.fixture
def mock_cloud():
    """Mocks the central Google Cloud Manager."""
    with patch('src.services.google_cloud.google_cloud.get_gemini_response', new_callable=AsyncMock) as m:
        yield m

@pytest.mark.asyncio
async def test_orchestrator_full_pipeline(mock_cloud):
    """Validates the full multi-agent flow through the orchestrator."""
    m = mock_cloud
    import json
    
    # Sequence of returns for the agents (Intent, Planner, Today, Explainer)
    m.side_effect = [
        json.dumps({"intent": "register", "category": "registration", "confidence": 0.9}), # Intent
        json.dumps({"steps": [{"title": "Verify ID", "description": "Check if your ID is valid.", "cta": "Check Now", "timeline_hint": "now"}]}), # Planner
        json.dumps({"action": "Verify Voter ID", "time_estimate": "2 mins", "urgency": "medium"}), # Today
        "This is a simplified explanation for registration." # Explainer
    ]
    
    orchestrator = Orchestrator()
    response = await orchestrator.handle_query(
        query="How to register?", 
        state="Texas", 
        mode=ExplanationMode.SIMPLE
    )
    
    assert response.state == "Texas"
    assert len(response.steps) == 1
    assert response.today_action.urgency == UrgencyLevel.MEDIUM
    assert len(response.reasoning_log) == 4
    assert "simplified" in response.final_explanation.lower()

@pytest.mark.asyncio
async def test_orchestrator_caching(mock_cloud):
    """Verifies that the Orchestrator LRU cache is working for efficiency."""
    m = mock_cloud
    import json
    m.return_value = json.dumps({"intent": "test", "category": "test", "confidence": 1.0})
    
    orchestrator = Orchestrator()
    # Call 1
    await orchestrator.handle_query("Cache Me", state="California")
    # Call 2 (Should not trigger another Gemini call)
    await orchestrator.handle_query("Cache Me", state="California")
    
    # Should only have been called for Intent, Planner, Today, Explainer once (4 times total)
    assert m.call_count == 4
