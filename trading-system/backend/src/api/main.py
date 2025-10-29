from fastapi import FastAPI
from src.api.routes import ingest, data

app = FastAPI()
app.include_router(ingest.router, prefix="/api")
app.include_router(data.router, prefix="/api")