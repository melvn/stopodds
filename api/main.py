from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession

from models import SubmissionCreate, OverviewResponse, PredictionResponse, MethodsResponse, GroupData, ModelType
from database import init_db, get_db
from services import SubmissionService, ModelService, AggregateService, PredictionService
from train import train_models
import pandas as pd
from sqlalchemy import text

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
async def submit_data(
    submission: SubmissionCreate, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get user agent for fraud detection
        user_agent = request.headers.get("user-agent", "")
        
        # Convert submission to dict and extract enum values 
        submission_data = submission.dict()
        
        # Convert enum objects to their string values
        for key, value in submission_data.items():
            if hasattr(value, 'value'):  # This is an enum
                submission_data[key] = value.value
        
        # Create submission
        result = await SubmissionService.create_submission(
            db, 
            submission_data, 
            user_agent
        )
        
        return {"status": "accepted", "id": str(result['id'])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/overview")
async def get_overview(db: AsyncSession = Depends(get_db)) -> OverviewResponse:
    try:
        # Get basic stats
        stats = await SubmissionService.get_submission_stats(db)
        
        # Get public aggregates
        aggregates = await AggregateService.get_public_aggregates(db)
        
        # Convert to response format
        groups = []
        for agg in aggregates:
            groups.append(GroupData(
                group_key=agg.group_key,
                n_people=agg.n_people,
                n_trips=agg.n_trips,
                n_stops=agg.n_stops,
                rate_per_100=agg.rate_per_100,
                irr_vs_ref=agg.irr_vs_ref,
                confidence_interval=[
                    agg.confidence_interval_lower, 
                    agg.confidence_interval_upper
                ] if agg.confidence_interval_lower is not None else None
            ))
        
        return OverviewResponse(
            total_submissions=stats['total_submissions'],
            total_trips=stats['total_trips'],
            total_stops=stats['total_stops'],
            groups=groups
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predict")
async def get_prediction(
    age_bracket: Optional[str] = None,
    gender: Optional[str] = None,
    ethnicity: Optional[str] = None,
    skin_tone: Optional[str] = None,
    height_bracket: Optional[str] = None,
    visible_disability: Optional[bool] = None,
    concession: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
) -> PredictionResponse:
    try:
        traits = {
            'age_bracket': age_bracket,
            'gender': gender,
            'ethnicity': ethnicity,
            'skin_tone': skin_tone,
            'height_bracket': height_bracket,
            'visible_disability': visible_disability,
            'concession': concession
        }
        
        # Remove None values
        traits = {k: v for k, v in traits.items() if v is not None}
        
        # Get personal estimate
        estimate = await PredictionService.get_personal_estimate(db, traits)
        
        return PredictionResponse(
            probability=estimate['probability'],
            confidence_interval=estimate['confidence_interval'],
            model_run_id=estimate['model_run_id'],
            explanation=estimate['explanation']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/methods")
async def get_methods(db: AsyncSession = Depends(get_db)) -> MethodsResponse:
    try:
        # Get latest model run
        latest_model = await ModelService.get_latest_model_run(db)
        
        # Get submission stats
        stats = await SubmissionService.get_submission_stats(db)
        
        if latest_model:
            return MethodsResponse(
                model_type=latest_model.model_type,
                last_trained=latest_model.created_at.isoformat(),
                sample_size=latest_model.train_rows,
                metrics=latest_model.metrics or {}
            )
        else:
            return MethodsResponse(
                model_type=ModelType.BASELINE,
                last_trained="",
                sample_size=stats['total_submissions'],
                metrics={
                    "note": "Insufficient data for ML training",
                    "min_required_submissions": 50,
                    "min_required_stops": 10,
                    "current_submissions": stats['total_submissions'],
                    "current_stops": stats['total_stops']
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/train")
async def train_model(db: AsyncSession = Depends(get_db)):
    """Train a new model with current data"""
    try:
        # Check if we have sufficient data
        requirements = await SubmissionService.check_minimum_requirements(db)
        
        if not requirements['meets_requirements']:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Insufficient data for training",
                    "requirements": requirements['requirements'],
                    "current_stats": requirements['stats']
                }
            )
        
        # Fetch all submission data
        result = await db.execute(text("""
            SELECT age_bracket, gender, ethnicity, skin_tone, height_bracket,
                   visible_disability, concession, trips, stops
            FROM submissions
            WHERE trips > 0 AND stops >= 0 AND stops <= trips
            ORDER BY created_at DESC
        """))
        
        rows = result.fetchall()
        if len(rows) == 0:
            raise HTTPException(status_code=400, detail="No valid training data found")
        
        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=[
            'age_bracket', 'gender', 'ethnicity', 'skin_tone', 'height_bracket',
            'visible_disability', 'concession', 'trips', 'stops'
        ])
        
        # Train models
        training_results = train_models(df)
        
        # Determine the primary model that was successfully trained
        primary_model = training_results.get('primary_model', 'baseline')
        
        if primary_model in ['lightgbm', 'negbin', 'poisson']:
            # Create model run record
            model_data = {
                'model_type': primary_model,
                'train_rows': len(df),
                'metrics': training_results.get(primary_model, {}).get('metrics', {}),
                'coefficients': training_results.get(primary_model, {}).get('coefficients', {}),
                'public_snapshot': True,
                'notes': f"Trained with {len(df)} submissions. Primary model: {primary_model}"
            }
            
            model_run = await ModelService.create_model_run(db, model_data)
            
            return {
                "status": "success",
                "model_type": primary_model,
                "model_run_id": str(model_run.run_id),
                "training_samples": len(df),
                "metrics": training_results.get(primary_model, {}).get('metrics', {}),
                "timestamp": model_run.created_at.isoformat()
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail={
                    "message": "Model training failed",
                    "errors": {
                        "lightgbm_error": training_results.get('lightgbm_error'),
                        "glm_error": training_results.get('glm_error')
                    }
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)