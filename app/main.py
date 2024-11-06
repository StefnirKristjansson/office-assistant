"""This is the main run file."""

import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.minnisblad import router as minnisblad_router
from app.routes.index import router as index_router

load_dotenv()

app = FastAPI()
app.include_router(minnisblad_router)
app.include_router(index_router)


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run("app.main:app", port=8080, reload=False, access_log=False)
