from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

load_dotenv()
bearer_token = os.getenv("BEARER_TOKEN")

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != bearer_token:
        raise HTTPException(status_code=403, detail="Invalid or missing token")

@router.get("/minnisblod", response_class=HTMLResponse)
async def minnisblod(request: Request, token: HTTPAuthorizationCredentials = Depends(verify_token)):
    return templates.TemplateResponse("minnisblod.html", {"request": request})
