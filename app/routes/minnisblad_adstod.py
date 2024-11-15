"""This module contains the routes for the minnisblad application."""

import os
import json
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
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils import get_token, extract_text_from_docx, send_text_to_openai, create_response_format

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key globally

OpenAI.api_key = openai_api_key
client = OpenAI()


@router.get("/minnisblad-adstod", response_class=HTMLResponse)
async def minnisblad_adstod(request: Request):
    """Render the minnisblad-adstod page."""
    return templates.TemplateResponse("minnisblad-adstod.html", {"request": request})


@router.post("/minnisblad-adstod/upload/")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    chapters: str = Form(...),
    _: str = Depends(get_token),
):
    """Process the uploaded file and return the JSON response."""
    if (
        file.content_type
        != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        or not file.filename.endswith(".docx")
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
        return JSONResponse(content=openai_response)
    except Exception as e:  # pylint: disable=broad-except
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": str(e)}
        )
