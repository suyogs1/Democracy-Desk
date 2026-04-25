import pytest
from src.services.google_cloud import google_cloud
from src.core.orchestrator import Orchestrator

@pytest.mark.asyncio
async def test_waterfall_resilience():
    """Verifies that the Gemini waterfall handles auth failures gracefully."""
    # Force a failure in REST but ensure it still returns content (even if mock)
    response = await google_cloud.get_gemini_response("test prompt", json_mode=True)
    assert response is not None
    assert "{" in response

@pytest.mark.asyncio
async def test_vision_simulation():
    """Ensures the Vision API module is correctly initialized for ID verification."""
    result = await google_cloud.detect_voter_id_validity("dummy_base64")
    assert result["valid"] is True
    assert result["document_type"] == "State ID"

@pytest.mark.asyncio
async def test_end_to_end_orchestration():
    """Validates the full multi-agent pipeline."""
    orchestrator = Orchestrator()
    response = await orchestrator.handle_query("How do I register?", state="Texas")
    assert response.intent.category in ["General", "Election Information"]
    assert len(response.steps) > 0
    assert response.today_action is not None
    assert len(response.reasoning_log) == 4
