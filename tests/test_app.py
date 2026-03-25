import pytest
from fastapi.testclient import TestClient
from govai.main import app

client = TestClient(app)

def test_health_check():
    """
    Test the health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_docs_accessible():
    """
    Ensure API documentation is accessible.
    """
    response = client.get("/docs")
    assert response.status_code == 200

def test_invalid_language():
    """
    Test ChatRequest validation with an unsupported language.
    """
    payload = {
        "message": "Hello",
        "language": "invalid_language_code"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 422
