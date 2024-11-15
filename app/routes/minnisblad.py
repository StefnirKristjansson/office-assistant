"""This module contains the routes for the minnisblad application."""

import os
from datetime import datetime
import json
from tempfile import NamedTemporaryFile
from fastapi import (
    APIRouter,
    Request,
    File,
    UploadFile,
    HTTPException,
    Form,
    Depends,
)
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils import get_token, extract_text_from_docx, send_text_to_openai, create_response_format

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

@router.get("/minnisblad", response_class=HTMLResponse)
async def minnisblad(request: Request):
    """Render the minnisblad page."""
    return templates.TemplateResponse("minnisblad.html", {"request": request})


@router.post("/minnisblad/upload/")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    chapters: str = Form(...),
    _: str = Depends(get_token),
):
    """Process the uploaded file and return the modified document."""
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
    except Exception as e:  # pylint: disable=broad-except
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": str(e)}
        )


def create_docx_from_json(response_json: dict) -> str:
    """Create a Word document from the JSON response."""
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

    # Save the document to a temporary file using 'with'
    with NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
        doc.save(temp_file.name)
        temp_file_path = temp_file.name  # Store the file path to return after closing

    return temp_file_path
