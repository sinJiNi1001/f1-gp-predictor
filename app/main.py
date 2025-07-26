# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.data_handler import get_lap_data, DataFetchError

app = FastAPI()

class PredictionRequest(BaseModel):
    year: int
    grand_prix: str

class PredictionResponse(BaseModel):
    predicted_winner: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionResponse)
async def predict_race(request: PredictionRequest):
    """Predict race winner endpoint"""
    try:
        session_data = get_lap_data(request.year, request.grand_prix)
        # TODO: Implement prediction logic
        return {"predicted_winner": "Max Verstappen"}  # Placeholder
    except DataFetchError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
