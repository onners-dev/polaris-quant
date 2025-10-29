from fastapi import FastAPI
from src.api.routes import ingest

app = FastAPI()
app.include_router(ingest.router, prefix="/api")
