"""This module contains the routes for the minnisblad application."""

import json
from fastapi import (
    APIRouter,
    Request,
    File,
    UploadFile,
    Depends,
    HTTPException,
)
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from app.utils import (
    send_text_to_openai,
    get_token,
    process_uploaded_file,
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
    file: UploadFile = File(...),
    _: str = Depends(get_token),
):
    """Process the uploaded file and return the JSON response."""
    text = await process_uploaded_file(file)
    try:
        respond_format = create_response_format()
        openai_response = await send_text_to_openai(text, respond_format)
        return JSONResponse(content=openai_response)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred"
        ) from e


def create_response_format() -> dict:
    """Create the response format based on the selected chapters."""
    base_response = {
        "type": "json_schema",
        "json_schema": {
            "name": "Minnisblad_adstod",
            "schema": {
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
