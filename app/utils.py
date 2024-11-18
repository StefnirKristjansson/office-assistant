"""Utility functions for the app."""

import os
import json
from docx import Document
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key globally

OpenAI.api_key = openai_api_key
client = OpenAI()


def extract_text_from_docx(file):
    """Extract text from a .docx file."""
    doc = Document(file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return "\n".join(text)


async def send_text_to_openai(
    text: str, response_format: dict
) -> dict:  # pragma: no cover
    """Send the text to the OpenAI API and return the response."""
    # Using the OpenAI client as per your original
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
