from fastapi import APIRouter, Request, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from docx import Document
from dotenv import load_dotenv
import os
from tempfile import NamedTemporaryFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

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
async def upload_file(request: Request, file: UploadFile = File(...)):
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
        openai_response = await send_text_to_openai(text)
        output_file_path = create_docx_from_text(openai_response)
        return FileResponse(
            output_file_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="OpenAI_Response.docx",
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


async def send_text_to_openai(text: str) -> str:
    # Using the OpenAI client as per your original code
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
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
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "minnisblað",
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
                            "Samantekt": {
                                "type": "string",
                                "description": "Samantekt minnisblaðsins.",
                        },
                    },
                    "required": ["title", "chapters"],
                    "additionalProperties": False,
                },
            },
        },
    )
    print(completion)
    return completion.choices[0].message.content


def create_docx_from_text(text: str) -> str:
    # Create a new Word document
    doc = Document()

    # Split the text into paragraphs based on double newlines
    paragraphs = text.split("\n\n")
    for para in paragraphs:
        doc.add_paragraph(para.strip())

    # Save the document to a temporary file
    temp_file = NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(temp_file.name)
    temp_file.close()
    return temp_file.name
