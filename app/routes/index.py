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


# Set the OpenAI API key globally
from openai import OpenAI

client = OpenAI()


@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
