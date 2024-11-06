"""This module defines the routes for the FastAPI application."""

from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """Render the index page."""
    return templates.TemplateResponse("index.html", {"request": request})
