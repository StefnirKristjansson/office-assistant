"""Test the routes in the FastAPI app."""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Get the .env token
BEARER_TOKEN = os.getenv("BEARER_TOKEN")


# Mock `send_text_to_openai` function directly
@pytest.fixture(autouse=True)
def mock_openai_response(mocker):
    """Mock the response from the OpenAI API."""
    mock_response = {
        "titill": "Test Title",
        "Inngangur": "Test Introduction",
        "kaflar": [{"chapter_title": "Test Chapter", "content": "Test Content"}],
        "Samantekt": "Test Summary",
    }
    mocker.patch(
        "app.routes.minnisblad.send_text_to_openai", return_value=mock_response
    )
    return mock_response


def test_upload_file_with_mocked_openai():
    """Test the upload_file route with a mocked OpenAI response."""
    with open("tests/test_document.docx", "rb") as file:
        token = BEARER_TOKEN
        response = client.post(
            "/minnisblad/upload/",
            files={
                "file": (
                    "test_document.docx",
                    file,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={"chapters": '["inngangur", "samantekt", "aaetlun"]'},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    # Ensure the response includes a docx file
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert response.content is not None


def test_upload_file_with_invalid_token():
    """Test the upload_file route with an invalid token."""
    with open("tests/test_document.docx", "rb") as file:
        token = "invalid_token"
        response = client.post(
            "/minnisblad/upload/",
            files={
                "file": (
                    "test_document.docx",
                    file,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={"chapters": '["inngangur", "samantekt", "aaetlun"]'},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token."}
