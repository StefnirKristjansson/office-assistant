"""This is the main run file."""

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.minnisblad import router as minnisblad_router
from app.routes.minnisblad_adstod import router as minnisblad_adstod_router
from app.routes.index import router as index_router

load_dotenv()

app = FastAPI()
app.include_router(minnisblad_router)
app.include_router(index_router)
app.include_router(minnisblad_adstod_router)


# serve static files
app.mount(
    "/static", StaticFiles(directory="app/static"), name="static"
)  # Ensure 'name' is set to "static"

if __name__ == "__main__":
    uvicorn.run("app.main:app", port=8080, reload=False, access_log=False)
