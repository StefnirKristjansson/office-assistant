from fastapi.testclient import TestClient
from app.main import app
import pytest
from unittest.mock import MagicMock
import openai

client = TestClient(app)

def test_upload_file():
    with open("tests/test_document.docx", "rb") as file:
        response = client.post("/upload/", files={"file": ("test_document.docx", file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    assert response.status_code == 200
    assert "text" in response.json()

@pytest.fixture
def mock_openai(mocker):
    mock_openai_client = mocker.patch("openai.OpenAI")
    mock_openai_instance = mock_openai_client.return_value
    mock_openai_instance.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"titill": "Test Title", "Inngangur": "Test Introduction", "kaflar": [{"chapter_title": "Test Chapter", "content": "Test Content"}], "Samantekt": "Test Summary"}'))]
    )
    return mock_openai_instance

def test_upload_file_with_mocked_openai(mock_openai):
    with open("tests/test_document.docx", "rb") as file:
        response = client.post("/upload/", files={"file": ("test_document.docx", file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert "OpenAI_Response" in response.headers["content-disposition"]
