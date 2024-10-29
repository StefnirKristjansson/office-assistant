from fastapi import APIRouter, Request, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from docx import Document
from dotenv import load_dotenv
import os
from openai import OpenAI

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key globally
OpenAI.api_key = openai_api_key


@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
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
    if word_count > 200000000000 or word_count < 1:
        raise HTTPException(
            status_code=400,
            detail="The document must contain between 1 and 2000 words.",
        )

    try:
        openai_response = await send_text_to_openai(text)
        return templates.TemplateResponse(
            "index.html", {"request": request, "openai_response": openai_response}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": str(e)}
        )


def extract_text_from_docx(file):
    doc = Document(file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return "\n".join(text)


async def send_text_to_openai(text: str) -> str:
    from openai import OpenAI

    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    OpenAI.api_key = openai_api_key
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "Það sem notandin er að senda er mynnisblað til ráðherra aðstoðaðu hann eftir bestu getu og gefðu ráðleggingar hvernig meigi bæta það",
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": text}],
            },
        ],
    )
    print(completion)

    return completion.choices[0].message.content
