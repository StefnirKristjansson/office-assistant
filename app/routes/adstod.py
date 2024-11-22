"""The route for adstod."""

import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
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
async def adstod_post():
    """Starts a thread for the assistan AI."""
    thread = client.beta.threads.create()
    thread_id = thread["id"] if isinstance(thread, dict) else thread.id
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content="Hver er markmið í nýustu geðheilbrigðisáætlun heilbrigðisráðuneitisins?",
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id="asst_rCMbGb73QwhMEvViv4laIoqD",
        instructions="Notandinn heytir Stefnir Húni Kristjánsson",
    )
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        data = messages.data
        message = data[0]
        text = message.content[0]
        a_message = text.text
        the_message = text.text.value
    else:
        return JSONResponse(
            content={"error": "The assistant did not complete the request."},
            status_code=500,
        )
    return JSONResponse(content={"content": the_message})
