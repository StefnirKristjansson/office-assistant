import os
import json
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")
OpenAI.api_key = openai_api_key
client = OpenAI()

token_auth_scheme = HTTPBearer()

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

def extract_text_from_docx(file):
    """Extract text from a .docx file."""
    doc = Document(file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return "\n".join(text)

async def send_text_to_openai(text: str, response_format: dict, content_text: str) -> dict:
    """Send the text to the OpenAI API and return the response."""
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

def create_response_format(selected_chapters: list, base_response: dict) -> dict:
    """Create the response format based on the selected chapters."""
    if "inngangur" in selected_chapters:
        base_response["json_schema"]["schema"]["properties"]["Inngangur"] = {
            "type": "string",
            "description": "Inngangur minnisblaðsins.",
        }
        base_response["json_schema"]["schema"]["required"].append("Inngangur")

    if "samantekt" in selected_chapters:
        base_response["json_schema"]["schema"]["properties"]["Samantekt"] = {
            "type": "string",
            "description": "Samantekt minnisblaðsins.",
        }
        base_response["json_schema"]["schema"]["required"].append("Samantekt")

    if "aaetlun" in selected_chapters:
        base_response["json_schema"]["schema"]["properties"]["Áætlun"] = {
            "type": "string",
            "description": "Áætlun minnisblaðsins.",
        }
        base_response["json_schema"]["schema"]["required"].append("Áætlun")

    if "markmid" in selected_chapters:
        base_response["json_schema"]["schema"]["properties"]["Markmið"] = {
            "type": "string",
            "description": "Markmið minnisblaðsins.",
        }
        base_response["json_schema"]["schema"]["required"].append("Markmið")

    return base_response
