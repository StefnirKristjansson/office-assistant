"""Test the routes in the FastAPI app."""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from tests.utils import (
    upload_file_with_invalid_token,
    upload_file_that_is_too_short,
    upload_wrong_file_type,
)
from app.utils import send_text_to_openai

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
        "aaetlun": "Test Plan",
        "markmid": "Test Objective",
    }
    mocker.patch(
        "app.routes.minnisblad.send_text_to_openai", return_value=mock_response
    )
    return mock_response


def test_upload_file_with_mocked_openai():  # pylint: disable=duplicate-code
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
            data={"chapters": '["inngangur", "samantekt", "aaetlun", "markmid"]'},
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
    response = upload_file_with_invalid_token("/minnisblad/upload/", client)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token."}


def test_upload_file_that_is_too_short():
    """Test the upload_file route with a document that is too short."""
    response = upload_file_that_is_too_short(
        "/minnisblad/upload/",
        client,
        data={"chapters": '["inngangur", "samantekt", "aaetlun", "markmid"]'},
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "The document must contain between 10 and 5000 words."
    }


def test_upload_wrong_file_type():
    """Test the upload_file route with a file that is not a .docx file."""
    response = upload_wrong_file_type(
        "/minnisblad/upload/",
        client,
        data={"chapters": '["inngangur", "samantekt", "aaetlun", "markmid"]'},
    )
    assert response.status_code == 400


def test_upload_file_unexpected_error(mocker):
    """Test the upload_file route when an unexpected error occurs."""
    # Mock send_text_to_openai to raise an exception
    mocker.patch(
        "app.routes.minnisblad.send_text_to_openai",
        side_effect=Exception("Test exception"),
    )

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
            data={"chapters": '["inngangur", "samantekt", "aaetlun", "markmid"]'},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 500
    assert response.json() == {"detail": "An unexpected error occurred"}


@pytest.mark.asyncio
async def test_send_text_to_openai(mocker):
    """Test the send_text_to_openai function."""
    # Mock the OpenAI client's chat completion create method
    mock_completion = mocker.Mock()
    mock_completion.choices = [mocker.Mock()]
    mock_completion.choices[0].message.content = '{"result": "Test Response"}'
    mocker.patch('app.utils.client.chat.completions.create', return_value=mock_completion)
    text = "This is a test text."
    response_format = {"type": "json"}
    response = await send_text_to_openai(text, response_format)
    assert response == {"result": "Test Response"}
