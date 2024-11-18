"""Utility functions for the app."""

import os
import json
from fastapi import (
    HTTPException,
    Depends,
    status,
    UploadFile
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dotenv import load_dotenv
from docx import Document
from openai import OpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key globally

OpenAI.api_key = openai_api_key
client = OpenAI()

BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Security scheme and token validation
token_auth_scheme = HTTPBearer()


def extract_text_from_docx(file):
    """Extract text from a .docx file."""
    doc = Document(file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return "\n".join(text)


async def send_text_to_openai(
    text: str, response_format: dict
) -> dict:
    """Send the text to the OpenAI API and return the response."""
    content_text = """Notendinn sendi þér minnisblað, farðu mjög varlega yfir það og
    finndu dæmi um önnur minnisblöð, 
    gefðu þér tíma að skoa Íslenskt málfar og stafsetningu."""
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": content_text,
                }
            ],
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": text}],
        },
    ]

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format=response_format,
    )
    response = json.loads(completion.choices[0].message.content)
    return response


def check_document_length(file) -> bool:
    """Check if the document is within the word limit and is a word document."""
    if (
        file.content_type
        != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        or not file.filename.endswith(".docx")
    ):
        return False
    file.file.seek(0)
    text = extract_text_from_docx(file.file)
    word_count = len(text.split())
    if word_count > 5000 or word_count < 10:
        return False
    return True


async def process_uploaded_file(file: UploadFile):
    """Helper function to process the uploaded file."""
    if not check_document_length(file):
        raise HTTPException(
            status_code=400,
            detail="The document must contain between 10 and 5000 words.",
        )
    file.file.seek(0)
    return extract_text_from_docx(file.file)


def get_token(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    """Validate the token and return it if it is valid."""
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme.",
        )
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
    return credentials.credentials
