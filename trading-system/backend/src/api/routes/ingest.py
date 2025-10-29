from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.ingestion.yahoo_ingest import ingest_yahoo

router = APIRouter()

class IngestRequest(BaseModel):
    tickers: List[str]
    start: str
    end: str
    interval: Optional[str] = "1d"

@router.post("/ingest")
def ingest(request: IngestRequest):
    try:
        result = ingest_yahoo(
            tickers=request.tickers,
            start=request.start,
            end=request.end,
            interval=request.interval,
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
