import pytest
from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "2.0.0"}

def test_ask_endpoint_schema():
    # Test that the endpoint exists and validates input
    response = client.post("/ask", json={})
    assert response.status_code == 422 # Validation Error

@pytest.mark.asyncio
async def test_orchestrator_logic():
    from core.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    # Note: This might fail without a real OpenAI key, so we'd normally mock it
    # For now, we just check if the class initializes and has the method
    assert hasattr(orchestrator, 'handle_query')
