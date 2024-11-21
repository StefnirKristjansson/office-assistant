"""The route for adstod."""

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from app.utils import process_uploaded_file, get_token

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/adstod")
async def adstod(request: Request):
    """Render the adstod page."""
    return templates.TemplateResponse("adstod.html", {"request": request})
