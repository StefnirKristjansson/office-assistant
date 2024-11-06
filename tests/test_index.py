"""Test the index route."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_index_returns():
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200
