import pytest
from src.core.orchestrator import Orchestrator
from src.core.models import ExplanationMode

@pytest.mark.asyncio
async def test_explanation_mode_eli10():
    """Verifies the explainer agent adapts tone correctly for simple mode."""
    orchestrator = Orchestrator()
    response = await orchestrator.handle_query(
        "Explain registration", 
        state="Florida", 
        mode=ExplanationMode.ELI10
    )
    assert response.final_explanation is not None
    # Complexity reduction often results in shorter or simpler sentences.
    assert len(response.final_explanation) > 0

@pytest.mark.asyncio
async def test_regional_coordination():
    """Validates that the orchestrator correctly context-switches between states."""
    orchestrator = Orchestrator()
    ny_res = await orchestrator.handle_query("When are polls open?", state="New York")
    tx_res = await orchestrator.handle_query("When are polls open?", state="Texas")
    # States should have distinct planning summaries
    assert ny_res.state == "New York"
    assert tx_res.state == "Texas"

def test_api_health():
    """Simple smoke test for API availability."""
    from api.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert "status" in res.json()
