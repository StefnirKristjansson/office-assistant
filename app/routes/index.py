import os

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from docx import Document
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize templates and router
templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """Render the index page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Handle file upload and process the document."""
    if (
        file.content_type
        != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a .docx file."
        )

    # Read and extract text from the uploaded .docx file
    file.file.seek(0)
    text = extract_text_from_docx(file.file)

    word_count = len(text.split())
    if not 1 <= word_count <= 2000:
        raise HTTPException(
            status_code=400,
            detail="The document must contain between 1 and 2000 words.",
        )

    try:
        openai_response = await send_text_to_openai(text)
        return templates.TemplateResponse(
            "index.html", {"request": request, "openai_response": openai_response}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": str(e)}
        )


def extract_text_from_docx(file) -> str:
    """Extract text from a .docx file."""
    doc = Document(file)
    text = [paragraph.text for paragraph in doc.paragraphs]
    return "\n".join(text)


async def send_text_to_openai(text: str) -> str:
    """Send text to OpenAI API and return the response."""
    completion = await openai.ChatCompletion.acreate(
        model="gpt-4", messages=[{"role": "user", "content": text}]
    )
    return completion.choices[0].message.content
