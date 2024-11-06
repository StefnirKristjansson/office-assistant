from fastapi import (
    APIRouter,
    Request,
    File,
    UploadFile,
    HTTPException,
    Form,
    Depends,
    status,
)
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from docx import Document
from dotenv import load_dotenv
import os
from typing import Annotated
from tempfile import NamedTemporaryFile
from fastapi.templating import Jinja2Templates
from datetime import datetime
import json

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Security scheme and token validation
token_auth_scheme = HTTPBearer()


def get_token(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
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


openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key globally
from openai import OpenAI

OpenAI.api_key = openai_api_key
client = OpenAI()


@router.get("/minnisblad", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("minnisblad.html", {"request": request})


@router.get("/minnisblad-adstod", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("minnisblad-adstod.html", {"request": request})


@router.post("/minnisblad/upload/")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    chapters: str = Form(...),
    token: str = Depends(get_token),
):
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
        respond_format = create_response_format(selected_chapters)
        openai_response = await send_text_to_openai(text, respond_format)
        # the openai_response is a string, so we need to convert it to a dictionary

        output_file_path = create_docx_from_json(openai_response)
        # create a timestamp in human readable format
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = "Frodi_minnisblad_" + timestamp + ".docx"

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


async def send_text_to_openai(text: str, response_format: dict) -> dict:
    # Using the OpenAI client as per your original code
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "Notandinn sendir þér texta sem þú átt að breyta í minnisblað. Bættu í og styttu textan eftir þörfum og kaflaskiftu eins og þú sérð best. Passaðu að hafa kaflanna ekki of stutta ekki hafa fleirri en 2 kafla á blaðsíðu.",
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
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format=response_format,
    )
    print(completion)
    response = json.loads(completion.choices[0].message.content)
    return response


def create_response_format(selected_chapters: list) -> dict:
    base_response = {
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
                },
                "required": [
                    "titill",
                    "kaflar",
                ],
                "additionalProperties": False,
            },
        },
    }
    inngangur_description = "Inngangur minnisblaðsins."
    samantekt_description = "Samantekt minnisblaðsins."
    aaetlun_description = "Áætlun minnisblaðsins."
    markmid_description = "Markmið minnisblaðsins."

    if "inngangur" in selected_chapters:
        base_response["json_schema"]["schema"]["properties"]["Inngangur"] = {
            "type": "string",
            "description": inngangur_description,
        }
        base_response["json_schema"]["schema"]["required"].append("Inngangur")

    if "samantekt" in selected_chapters:
        base_response["json_schema"]["schema"]["properties"]["Samantekt"] = {
            "type": "string",
            "description": samantekt_description,
        }
        base_response["json_schema"]["schema"]["required"].append("Samantekt")

    if "aaetlun" in selected_chapters:
        base_response["json_schema"]["schema"]["properties"]["Áætlun"] = {
            "type": "string",
            "description": aaetlun_description,
        }
        base_response["json_schema"]["schema"]["required"].append("Áætlun")

    if "markmid" in selected_chapters:
        base_response["json_schema"]["schema"]["properties"]["Markmið"] = {
            "type": "string",
            "description": markmid_description,
        }
        base_response["json_schema"]["schema"]["required"].append("Markmið")

    return base_response


def create_docx_from_json(response_json: dict) -> str:
    # Create a new Word document
    doc = Document()

    # Add the title
    doc.add_heading(response_json.get("titill", "Titill Ekki Tiltækur"), level=1)

    # if there is an introduction, add it to the document
    if "Inngangur" in response_json:
        doc.add_heading("Inngangur", level=2)
        doc.add_paragraph(response_json["Inngangur"])

    # if there is markmid, add it to the document
    if "Markmið" in response_json:
        doc.add_heading("Markmið", level=2)
        doc.add_paragraph(response_json["Markmið"])

    if "Áætlun" in response_json:
        doc.add_heading("Áætlun", level=2)
        doc.add_paragraph(response_json["Áætlun"])

    # if there are chapters, add them to the document
    if "kaflar" in response_json:
        for chapter in response_json["kaflar"]:
            doc.add_heading(chapter["chapter_title"], level=2)
            doc.add_paragraph(chapter["content"])

    # if there is a summary, add it to the document
    if "Samantekt" in response_json:
        doc.add_heading("Samantekt", level=2)
        doc.add_paragraph(response_json["Samantekt"])

    # Save the document to a temporary file
    temp_file = NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(temp_file.name)
    temp_file.close()
    return temp_file.name
