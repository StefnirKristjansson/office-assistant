"""This module contains the routes for the minnisblad application."""

from datetime import datetime
import json
from tempfile import NamedTemporaryFile
from fastapi import (
    APIRouter,
    Request,
    File,
    UploadFile,
    Form,
    Depends,
)
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from docx import Document
from app.utils import (
    send_text_to_openai,
    get_token,
    process_uploaded_file,  # Add the import
)


templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


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
    text = await process_uploaded_file(file)
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


def create_response_format(selected_chapters: list) -> dict:
    """Create the response format based on the selected chapters."""
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
