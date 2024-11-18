"""This module contains the routes for the minnisblad application."""

from fastapi import (
    APIRouter,
    Request,
    File,
    UploadFile,
    HTTPException,
    Depends,
)
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from app.utils import (
    extract_text_from_docx,
    send_text_to_openai,
    check_document_lenght,
    get_token,
)


templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

load_dotenv()


@router.get("/minnisblad-adstod", response_class=HTMLResponse)
async def minnisblad_adstod(request: Request):
    """Render the minnisblad-adstod page."""
    return templates.TemplateResponse("minnisblad-adstod.html", {"request": request})


@router.post("/minnisblad-adstod/upload/")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    _: str = Depends(get_token),
):
    """Process the uploaded file and return the JSON response."""
    if not check_document_lenght(file):
        raise HTTPException(
            status_code=400,
            detail="The document must contain between 10 and 5000 words.",
        )
    file.file.seek(0)
    text = extract_text_from_docx(file.file)

    try:
        respond_format = create_response_format()
        openai_response = await send_text_to_openai(text, respond_format)
        return JSONResponse(content=openai_response)
    except Exception as e:  # pylint: disable=broad-except
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": str(e)}
        )


def create_response_format() -> dict:
    """Create the response format based on the selected chapters."""
    base_response = base_response = {
        "type": "json_schema",
        "json_schema": {
            "name": "Minnisblad_adstod",
            "schema": {  # Correcting to include 'schema' directly
                "title": "Minnisblad_adstod",
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the schema"},
                    "type": {
                        "type": "string",
                        "enum": [
                            "object",
                            "array",
                            "string",
                            "number",
                            "boolean",
                            "null",
                        ],
                        "description": "The type of the schema (should match JSON Schema types)",
                    },
                    "properties": {
                        "type": "object",
                        "properties": {
                            "malfar": {
                                "type": "string",
                                "description": """Hérna setur þú inn hvað meigi bæta og
                                breyta varðandi málfar,
                                stíl og uppbyggingu minnisblaðsins.""",
                            },
                            "stafsetning": {
                                "type": "string",
                                "description": """Hérna setur þú inn hvað meigi bæta og
                                breyta varðandi stafsetningu passaðu
                                að benda skýrt á allar stafsetningarvillur
                                með að vitna í textan sem á við.""",
                            },
                            "radleggingar": {
                                "type": "string",
                                "description": """Hérna setur þú inn hvað meigi bæta og
                                breyta varðandi almennar raðleggingar.
                                Farðu vel yfir hvernig minnisblöð eru yfir höfuð
                                og hafðu það í huga""",
                            },
                        },
                        "required": ["malfar", "stafsetning", "radleggingar"],
                        "additionalProperties": False,
                    },
                },
                "required": ["name", "type", "properties"],
                "additionalProperties": False,
            },
        },
    }

    return base_response
