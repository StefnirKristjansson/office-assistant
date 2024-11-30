"""The route for adstod."""

import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key globally

OpenAI.api_key = openai_api_key
client = OpenAI()

chat_history = {}


class UserMessage(BaseModel):
    message: str


@router.get("/adstod")
async def adstod(request: Request):
    """Render the adstod page."""
    return templates.TemplateResponse("adstod.html", {"request": request})


@router.post("/adstod/start")
async def adstod_post(user_message: UserMessage, request: Request):
    """Starts a thread for the assistant AI."""
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in chat_history:
        thread = client.beta.threads.create()
        thread_id = thread["id"] if isinstance(thread, dict) else thread.id
        chat_history[session_id] = {"thread_id": thread_id, "messages": []}
    else:
        thread_id = chat_history[session_id]["thread_id"]

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message.message,
    )
    chat_history[session_id]["messages"].append({"role": "user", "content": user_message.message})

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
        the_message = text.text.value
        chat_history[session_id]["messages"].append({"role": "assistant", "content": the_message})
    else:
        return JSONResponse(
            content={"error": "The assistant did not complete the request."},
            status_code=500,
        )
    return JSONResponse(content={"content": the_message, "history": chat_history[session_id]["messages"]})
