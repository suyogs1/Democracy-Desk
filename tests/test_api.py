import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_root_redirect():
    """Verifies the UI redirect."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/ui/index.html"

def test_health_endpoint():
    """Verifies the expanded health check."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_security_headers():
    """Verifies 95+ score security headers are present."""
    response = client.get("/health")
    assert "Content-Security-Policy" in response.headers
    assert "Strict-Transport-Security" in response.headers
    assert "X-Content-Type-Options" in response.headers
    assert "X-Download-Options" in response.headers

def test_efficiency_headers():
    """Verifies efficiency/performance headers."""
    response = client.get("/health")
    assert "X-Process-Time" in response.headers
    # Note: Gzip might not trigger on a tiny health response, but the middleware is active.
