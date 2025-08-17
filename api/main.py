from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from models import SubmissionCreate, OverviewResponse, PredictionResponse, MethodsResponse
from database import init_db

app = FastAPI(
    title="StopOdds API",
    description="API for Melbourne public transport stop rate estimation",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "StopOdds API", "version": "0.1.0"}

@app.post("/api/submit")
async def submit_data(submission: SubmissionCreate):
    # TODO: Implement submission logic
    return {"status": "accepted"}

@app.get("/api/overview")
async def get_overview() -> OverviewResponse:
    # TODO: Implement overview logic
    return OverviewResponse(
        total_submissions=0,
        total_trips=0,
        total_stops=0,
        groups=[]
    )

@app.get("/api/predict")
async def get_prediction(
    age_bracket: Optional[str] = None,
    gender: Optional[str] = None,
    ethnicity: Optional[str] = None,
    skin_tone: Optional[str] = None,
    height_bracket: Optional[str] = None,
    visible_disability: Optional[bool] = None,
    concession: Optional[bool] = None
) -> PredictionResponse:
    # TODO: Implement prediction logic
    return PredictionResponse(
        probability=0.0,
        confidence_interval=[0.0, 0.0],
        model_run_id="",
        explanation=[]
    )

@app.get("/api/methods")
async def get_methods() -> MethodsResponse:
    # TODO: Implement methods logic
    return MethodsResponse(
        model_type="poisson",
        last_trained="",
        sample_size=0,
        metrics={}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)