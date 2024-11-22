import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils import send_text_to_openai
from tests.utils import (
    upload_file_with_invalid_token,
    upload_file_that_is_too_short,
    upload_wrong_file_type,
    upload_file_with_mocked_openai,
)

from tests.utils import (
    upload_file_with_invalid_token,
    upload_file_that_is_too_short,
    upload_wrong_file_type,
    upload_file_with_mocked_openai,
)

client = TestClient(app)
from pydantic import BaseModel


class Run(BaseModel):
    """A run object."""

    status: str


class Messages(BaseModel):
    """A messages object."""

    data: list


class Message(BaseModel):
    """A message object."""

    content: list


class Value(BaseModel):
    """A value object."""

    value: str


class Text(BaseModel):
    """A text object."""

    text: Value


@pytest.fixture(autouse=True)
def mock_openai_assistant(mocker):
    """Mock the response from the OpenAI API."""
    mocker.patch(
        "app.routes.adstod.client.beta.threads.create", return_value={"id": "Test ID"}
    )
    mocker.patch(
        "app.routes.adstod.client.beta.threads.messages.create",
        return_value="Test Message",
    )
    mocker.patch(
        "app.routes.adstod.client.beta.threads.runs.create_and_poll",
        return_value=Run(status="completed"),
    )
    mocker.patch(
        "app.routes.adstod.client.beta.threads.messages.list",
        return_value=Messages(
            data=[Message(content=[Text(text=Value(value="Test Content"))])]
        ),
    )
    return "Test Content"


def test_send_message_to_adstod():
    """Test the post adstod route and mock the OpenAI response."""
    response = client.post("/adstod/start")
    assert response.status_code == 200
    assert response.json() == {"content": "Test Content"}


def test_adstod_page():
    """Test the get adstod route."""
    response = client.get("/adstod")
    assert response.status_code == 200
    assert "<title>Fróði</title>" in response.text


def test_adstod_post_thread_creation_failure(mocker):
    """Test the post adstod route when thread creation fails."""
    mocker.patch(
        "app.routes.adstod.client.beta.threads.create",
        side_effect=Exception("Failed to create thread"),
    )
    response = client.post("/adstod/start")
    assert response.status_code == 500
    assert response.json() == {"error": "The assistant did not complete the request."}


def test_adstod_post_run_failure(mocker):
    """Test the post adstod route when run creation fails."""
    mocker.patch(
        "app.routes.adstod.client.beta.threads.runs.create_and_poll",
        return_value={"status": "failed"},
    )
    response = client.post("/adstod/start")
    assert response.status_code == 500
    assert response.json() == {"error": "The assistant did not complete the request."}
