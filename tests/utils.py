"""The utility functions for tests."""

import os
from fastapi.testclient import TestClient


BEARER_TOKEN = os.getenv("BEARER_TOKEN")


def upload_file_with_invalid_token(url: str, client: TestClient) -> dict:
    """Test the upload_file route with an invalid token."""
    with open("tests/test_document.docx", "rb") as file:
        token = "invalid_token"
        response = client.post(
            f"{url}",
            files={
                "file": (
                    "test_document.docx",
                    file,
                    "text/plain",
                )
            },
            headers={"Authorization": f"Bearer {token}"},
        )
    return response


def upload_file_that_is_too_short(
    url: str, client: TestClient, data: dict = None
) -> dict:
    """Test the upload_file route with a document that is too short."""
    if data is None:
        data = {}
    with open("tests/test_document_short.docx", "rb") as file:
        token = BEARER_TOKEN
        response = client.post(
            f"{url}",
            files={
                "file": (
                    "test_document_short.docx",
                    file,
                    "text/plain",
                )
            },
            data=data,
            headers={"Authorization": f"Bearer {token}"},
        )
    return response


def upload_wrong_file_type(url: str, client: TestClient, data: dict = None) -> dict:
    """Test the upload_file route with a file that is not a .docx file."""
    if data is None:
        data = {}
    with open("tests/test_document.txt", "rb") as file:
        token = BEARER_TOKEN

        response = client.post(
            f"{url}",
            files={
                "file": (
                    "test_document.txt",
                    file,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data=data,
            headers={"Authorization": f"Bearer {token}"},
        )
    return response


def upload_file_with_mocked_openai(url, client):
    """
    Test the upload_file route with a mocked OpenAI response.

    Args:
        url (str): The endpoint URL.
        client: The test client to send requests.
        mocker: The pytest-mock mocker object for mocking dependencies.
    """
    with open("tests/test_document.docx", "rb") as file:
        token = BEARER_TOKEN
        response = client.post(
            f"{url}",
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
    return response
