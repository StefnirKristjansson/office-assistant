import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Mock `send_text_to_openai` function directly
@pytest.fixture
def mock_openai_response(mocker):
    mock_response = {
        "titill": "Test Title",
        "Inngangur": "Test Introduction",
        "kaflar": [{"chapter_title": "Test Chapter", "content": "Test Content"}],
        "Samantekt": "Test Summary",
    }
    mocker.patch("app.routes.index.send_text_to_openai", return_value=mock_response)
    return mock_response


def test_upload_file_with_mocked_openai(mock_openai_response):
    with open("tests/test_document.docx", "rb") as file:
        response = client.post(
            "/upload/",
            files={
                "file": (
                    "test_document.docx",
                    file,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={"chapters": '["inngangur", "samantekt", "aaetlun"]'},
        )
    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert "OpenAI_Response" in response.headers["content-disposition"]


def test_minnisblod_route_with_valid_token():
    response = client.get("/minnisblod", headers={"Authorization": "Bearer your_token_here"})
    assert response.status_code == 200
    assert "Please enter the bearer token to access this page." in response.text


def test_minnisblod_route_with_invalid_token():
    response = client.get("/minnisblod", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid or missing token"}
