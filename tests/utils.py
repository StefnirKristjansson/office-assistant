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


def upload_file_that_is_too_short(url: str, client: TestClient) -> dict:
    """Test the upload_file route with a document that is too short."""
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
            headers={"Authorization": f"Bearer {token}"},
        )
    return response


def upload_wrong_file_type(url: str, client: TestClient) -> dict:
    """Test the upload_file route with a file that is not a .docx file."""
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
            headers={"Authorization": f"Bearer {token}"},
        )
    return response
