from fastapi import FastAPI
from src.api.routes import ingest, data, clean, features, raw, features_data, table, models

app = FastAPI()
app.include_router(ingest.router, prefix="/api")
app.include_router(data.router, prefix="/api")
app.include_router(clean.router, prefix="/api")
app.include_router(features.router, prefix="/api")
app.include_router(raw.router, prefix="/api")
app.include_router(features_data.router, prefix="/api")
app.include_router(table.router, prefix="/api")
app.include_router(models.router, prefix="/api")