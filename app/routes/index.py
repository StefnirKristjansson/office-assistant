from fastapi import APIRouter, Request, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from docx import Document
from dotenv import load_dotenv
import os
from tempfile import NamedTemporaryFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import datetime
import json

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key globally
from openai import OpenAI

OpenAI.api_key = openai_api_key
client = OpenAI()


@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...), chapters: str = Form(...)):
    if (
        file.content_type
        != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a .docx file."
        )

    # Ensure the file pointer is at the beginning
    file.file.seek(0)
    text = extract_text_from_docx(file.file)

    word_count = len(text.split())
    if word_count > 5000 or word_count < 10:
        raise HTTPException(
            status_code=400,
            detail="The document must contain between 10 and 5000 words.",
        )

    try:
        selected_chapters = json.loads(chapters)
        openai_response = await send_text_to_openai(text, selected_chapters)
        # the openai_response is a string, so we need to convert it to a dictionary

        output_file_path = create_docx_from_json(openai_response)
        # create a timestamp in human readable format
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = "OpenAI_Response_" + timestamp + ".docx"

        return FileResponse(
            output_file_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": str(e)}
        )


def extract_text_from_docx(file):
    doc = Document(file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return "\n".join(text)


async def send_text_to_openai(text: str, selected_chapters: list) -> json:
    # Using the OpenAI client as per your original code
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "Notandinn sendir þér texta sem þú átt að breyta í minnisblað. Bættu í og styttu textan eftir þörfum og kaflaskiftu eins og þú sérð best",
                }
            ],
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": text}],
        },
    ]

    # Add selected chapters to the system message
    if selected_chapters:
        chapter_text = "Notandinn vill að eftirfarandi kaflar séu bættir við: " + ", ".join(selected_chapters)
        messages[0]["content"].append({"type": "text", "text": chapter_text})

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "minnisblad",  # Updated name
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "titill": {
                            "type": "string",
                            "description": "Titill minnisblaðsins.",
                        },
                        "Inngangur": {
                            "type": "string",
                            "description": "Inngangur minnisblaðsins.",
                        },
                        "kaflar": {
                            "type": "array",
                            "description": "Kaflar minnisblaðsins.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "chapter_title": {
                                        "type": "string",
                                        "description": "Titill kafla.",
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "Innihald kafla.",
                                    },
                                },
                                "required": ["chapter_title", "content"],
                                "additionalProperties": False,
                            },
                        },
                        "Samantekt": {
                            "type": "string",
                            "description": "Samantekt minnisblaðsins.",
                        },
                    },
                    "required": [
                        "titill",
                        "kaflar",
                        "Inngangur",
                        "Samantekt",
                    ],  # Added required fields
                    "additionalProperties": False,
                },
            },
        },
    )
    print(completion)
    response = json.loads(completion.choices[0].message.content)
    return response


def create_docx_from_json(response_json: dict) -> str:
    # Create a new Word document
    doc = Document()

    # Add the title
    doc.add_heading(response_json.get("titill", "Titill Ekki Tiltækur"), level=1)

    # Add the introduction
    doc.add_paragraph(response_json.get("Inngangur", ""))

    # Add chapters
    for chapter in response_json.get("kaflar", []):
        doc.add_heading(chapter.get("chapter_title", "Kafli"), level=2)
        doc.add_paragraph(chapter.get("content", ""))

    # Add the summary
    doc.add_heading("Samantekt", level=2)
    doc.add_paragraph(response_json.get("Samantekt", ""))

    # Save the document to a temporary file
    temp_file = NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(temp_file.name)
    temp_file.close()
    return temp_file.name
