"""The route for adstod."""

import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from app.utils import process_uploaded_file, get_token
from fastapi.responses import JSONResponse

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key globally

OpenAI.api_key = openai_api_key
client = OpenAI()


@router.get("/adstod")
async def adstod(request: Request):
    """Render the adstod page."""
    return templates.TemplateResponse("adstod.html", {"request": request})


@router.post("/adstod/start")
async def adstod_post(request: Request):
    """Starts a thread for the assistan AI."""
    thread = client.beta.threads.create()
    print(thread)
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Segðu mér frá stefnuáætlun heilbrigðisráðuneiðisins",
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id="asst_rCMbGb73QwhMEvViv4laIoqD",
        instructions="Notandinn heytir Stefnir Húni Kristjánsson",
    )
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print(messages)
        # get the last message
        data = messages.data
        message = data[0]
        text = message.content[0]
        the_message = text.text.value
        return JSONResponse(content={"content": the_message})
    else:
        print(run.status)
        return JSONResponse(
            content={"error": "The assistant did not complete the request."},
            status_code=500,
        )
