from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.models.train_xgboost_tidy import ModelTrainer
from src.utils.json_safe import clean_for_json

router = APIRouter()

class TrainRequest(BaseModel):
    tickers: Optional[List[str]]
    target: str = "Return_1d"

@router.post("/models/train")
def train_model(req: TrainRequest):
    try:
        trainer = ModelTrainer(tickers=req.tickers, target_col=req.target)
        result = trainer.run()
        return {"success": True, "model": clean_for_json(result)}
    except Exception as e:
        import traceback
        print("Error in model train endpoint:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
