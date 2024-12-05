"""Routes for the adstod page."""

import os
import re
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
    """A user message object."""

    message: str
    thread_id: str = None


def process_message(the_message):
    """Process the message content to replace references and prepare the modified message."""
    # Find content inside 【 】 and handle duplicates
    pattern = r"【.*?†(.*?)】"
    matches = re.findall(pattern, the_message)

    file_map = {}
    current_index = 1

    # Create a mapping for files with unique numeric indices
    for file in matches:
        if file not in file_map:
            file_map[file] = current_index
            current_index += 1

    # Replace references with indices
    def replace_files_with_indices(match):
        file_name = match.group(1)
        return f"【{file_map[file_name]}】"

    text_with_indices = re.sub(
        r"【.*?†(.*?)】", replace_files_with_indices, the_message
    )

    # Prepare sources list
    sources_list = "\n".join([f"{index}: {file}" for file, index in file_map.items()])

    # If there are no sources, don't add the sources list
    if not sources_list:
        modified_message = text_with_indices
    else:
        modified_message = f"{text_with_indices}\n\nSources:\n{sources_list}"

    return modified_message


@router.get("/adstod")
async def adstod(request: Request):
    """Render the adstod page."""
    return templates.TemplateResponse("adstod.html", {"request": request})


@router.post("/adstod/start")
async def adstod_post(user_message: UserMessage):
    """Starts a thread for the assistant AI."""
    thread_id = user_message.thread_id
    # Start by checking if the thread_id is None or empty
    if not thread_id:
        thread = client.beta.threads.create()
        thread_id = thread.id

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message.message,
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id="asst_rCMbGb73QwhMEvViv4laIoqD",
        instructions="Notandinn heytir Stefnir Húni Kristjánsson",
    )
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        the_message = messages.data[0].content[0].text.value
        modified_message = process_message(the_message)
    else:
        return JSONResponse(
            content={"error": "The assistant did not complete the request."},
            status_code=500,
        )
    return JSONResponse(
        content={
            "message": modified_message,
            "thread_id": thread_id,
        }
    )
