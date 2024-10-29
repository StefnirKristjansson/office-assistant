from fastapi import APIRouter, Request, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from docx import Document

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if (
        file.content_type
        != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a .docx file."
        )

    # Ensure the file pointer is at the beginning
    file.file.seek(0)
    text = extract_text_from_docx(file.file)

    word_count = len(text.split())
    if word_count > 2000 or word_count < 1:
        raise HTTPException(
            status_code=400, detail="The document must contain between 1 and 20 words."
        )

    return {"text": text}


def extract_text_from_docx(file):
    doc = Document(file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return "\n".join(text)
