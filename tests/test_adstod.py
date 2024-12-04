"""Test the adstod routes."""

import pytest
from pydantic import BaseModel
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class thread(BaseModel):
    """A thread object."""

    id: str


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
        "app.routes.adstod.client.beta.threads.create", return_value=thread(id="3421")
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
    response = client.post(
        "/adstod/start", json={"message": "Hello", "thread_id": "3421_test"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Test Content",
        "thread_id": "3421_test",
    }


def test_send_message_to_adstod_without_session_id():
    """Test the post adstod route without a session id."""
    response = client.post("/adstod/start", json={"message": "Hello"})
    assert response.status_code == 200
    # There shuld be a session id in the response
    assert "thread_id" in response.json()


def test_adstod_page():
    """Test the get adstod route."""
    response = client.get("/adstod")
    assert response.status_code == 200
    assert "<title>Fróði</title>" in response.text
