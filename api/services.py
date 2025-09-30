from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from models import Submission, ModelRun, AggregatePublic
from database import get_db
from train import StopOddsModeler
from adaptive_ml import AdaptiveMLPipeline
import hashlib
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import glob

class SubmissionService:
    @staticmethod
    async def create_submission(db: AsyncSession, submission_data: dict, user_agent: str = None) -> dict:
        """Create a new submission with hashed user agent using raw SQL"""
        # Hash user agent with daily salt for fraud detection
        user_agent_hash = None
        if user_agent:
            daily_salt = datetime.now().strftime("%Y-%m-%d") + "stopodds_salt"
            user_agent_hash = hashlib.sha256(f"{user_agent}{daily_salt}".encode()).hexdigest()
        
        from sqlalchemy import text
        import uuid
        
        submission_id = uuid.uuid4()
        
        # Use raw SQL to insert data
        await db.execute(text("""
            INSERT INTO submissions (id, age_bracket, gender, ethnicity, skin_tone, height_bracket, 
                                   visible_disability, concession, trips, stops, user_agent_hash)
            VALUES (:id, :age_bracket, :gender, :ethnicity, :skin_tone, :height_bracket,
                    :visible_disability, :concession, :trips, :stops, :user_agent_hash)
        """), {
            'id': submission_id,
            'age_bracket': submission_data.get('age_bracket'),
            'gender': submission_data.get('gender'), 
            'ethnicity': submission_data.get('ethnicity'),
            'skin_tone': submission_data.get('skin_tone'),
            'height_bracket': submission_data.get('height_bracket'),
            'visible_disability': submission_data.get('visible_disability'),
            'concession': submission_data.get('concession'),
            'trips': submission_data['trips'],
            'stops': submission_data['stops'],
            'user_agent_hash': user_agent_hash
        })
        
        await db.commit()
        return {'id': submission_id}
    
    @staticmethod
    async def get_submission_stats(db: AsyncSession) -> Dict[str, int]:
        """Get basic submission statistics"""
        result = await db.execute(
            select(
                func.count(Submission.id).label('total_submissions'),
                func.sum(Submission.trips).label('total_trips'),
                func.sum(Submission.stops).label('total_stops')
            )
        )
        stats = result.first()
        return {
            'total_submissions': stats.total_submissions or 0,
            'total_trips': stats.total_trips or 0,
            'total_stops': stats.total_stops or 0
        }
    
    @staticmethod
    async def check_minimum_requirements(db: AsyncSession) -> Dict[str, Any]:
        """Check if we have minimum data for adaptive ML training"""
        stats = await SubmissionService.get_submission_stats(db)

        # Much lower requirements for adaptive ML (scales with data size)
        min_submissions = 50
        min_stops = 10

        meets_requirements = (
            stats['total_submissions'] >= min_submissions and
            stats['total_stops'] >= min_stops
        )

        # Determine model tier based on sample size
        model_tier = "regularized_linear"
        if stats['total_submissions'] >= 100:
            model_tier = "single_tree"
        elif stats['total_submissions'] >= 300:
            model_tier = "ensemble"
        elif stats['total_submissions'] >= 1000:
            model_tier = "full_ml"

        return {
            'meets_requirements': meets_requirements,
            'stats': stats,
            'requirements': {
                'min_submissions': min_submissions,
                'min_stops': min_stops
            },
            'model_type': 'adaptive_ml',
            'predicted_tier': model_tier
        }

class ModelService:
    @staticmethod
    async def get_latest_model_run(db: AsyncSession) -> Optional[ModelRun]:
        """Get the latest public model run"""
        result = await db.execute(
            select(ModelRun)
            .where(ModelRun.public_snapshot == True)
            .order_by(ModelRun.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_model_run(db: AsyncSession, model_data: Dict[str, Any]) -> ModelRun:
        """Create a new model run record"""
        model_run = ModelRun(
            model_type=model_data['model_type'],
            train_rows=model_data['train_rows'],
            metrics=model_data['metrics'],
            coeffs=model_data['coefficients'],
            public_snapshot=model_data.get('public_snapshot', False),
            notes=model_data.get('notes', '')
        )
        
        db.add(model_run)
        await db.commit()
        await db.refresh(model_run)
        return model_run

class AggregateService:
    @staticmethod
    async def get_public_aggregates(db: AsyncSession, model_run_id: Optional[str] = None) -> List[AggregatePublic]:
        """Get public aggregates for the latest or specified model run"""
        query = select(AggregatePublic)
        
        if model_run_id:
            query = query.where(AggregatePublic.model_run_id == model_run_id)
        else:
            # Get aggregates for the latest public model run
            latest_model = await ModelService.get_latest_model_run(db)
            if latest_model:
                query = query.where(AggregatePublic.model_run_id == latest_model.run_id)
            else:
                return []
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def create_aggregates(db: AsyncSession, aggregates_data: List[Dict[str, Any]], model_run_id: str):
        """Create public aggregates from model results"""
        # Clear existing aggregates for this model run
        await db.execute(
            select(AggregatePublic).where(AggregatePublic.model_run_id == model_run_id)
        )
        
        # Create new aggregates
        for agg_data in aggregates_data:
            if agg_data['n_people'] >= 50:  # k-anonymity check
                aggregate = AggregatePublic(
                    group_key=agg_data['group_key'],
                    n_people=agg_data['n_people'],
                    n_trips=agg_data['n_trips'],
                    n_stops=agg_data['n_stops'],
                    rate_per_100=agg_data['rate_per_100'],
                    irr_vs_ref=agg_data.get('irr_vs_ref'),
                    confidence_interval_lower=agg_data.get('ci_lower'),
                    confidence_interval_upper=agg_data.get('ci_upper'),
                    model_run_id=model_run_id
                )
                db.add(aggregate)
        
        await db.commit()

class PredictionService:
    _cached_model = None
    _cached_adaptive_model = None
    _model_timestamp = None
    _adaptive_timestamp = None
    
    @staticmethod
    def calculate_baseline_estimate(traits: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate a simple baseline estimate when no model is available"""
        # Enhanced baseline with simple trait adjustments
        base_rate = 8.5  # Base rate per 100 trips
        
        # Simple adjustments based on traits
        if traits.get('concession'):
            base_rate *= 0.85  # Concession users checked less
        
        if traits.get('age_bracket') == '18-24':
            base_rate *= 1.15  # Young adults checked more
        elif traits.get('age_bracket') == '45+':
            base_rate *= 0.95  # Older adults checked slightly less
        
        if traits.get('visible_disability'):
            base_rate *= 0.8  # Visible disability may reduce checks
        
        # Cap at reasonable bounds
        base_rate = max(2.0, min(base_rate, 20.0))
        confidence_interval = [max(1.0, base_rate - 3.0), base_rate + 3.0]
        
        explanation = [
            "Based on limited data from Melbourne commuters",
            "Simple adjustments made for your demographic profile",
            "Accuracy will improve as more data is collected"
        ]
        
        return {
            'probability': round(base_rate, 1),
            'confidence_interval': [round(ci, 1) for ci in confidence_interval],
            'model_run_id': 'baseline',
            'explanation': explanation,
            'is_baseline': True
        }
    
    @staticmethod
    def load_latest_adaptive_model() -> Optional[AdaptiveMLPipeline]:
        """Load the most recent adaptive ML model"""
        try:
            # Find the latest adaptive model file
            model_files = glob.glob("/tmp/stopodds_adaptive_model_*.pkl")
            if not model_files:
                return None

            # Get the most recent model
            latest_model = max(model_files, key=os.path.getctime)

            # Check if we need to reload (cache for 1 hour)
            model_time = os.path.getctime(latest_model)
            if (PredictionService._cached_adaptive_model is None or
                PredictionService._adaptive_timestamp is None or
                model_time > PredictionService._adaptive_timestamp):

                adaptive_model = AdaptiveMLPipeline()
                adaptive_model.load_model(latest_model)

                PredictionService._cached_adaptive_model = adaptive_model
                PredictionService._adaptive_timestamp = model_time

            return PredictionService._cached_adaptive_model

        except Exception as e:
            print(f"Error loading adaptive model: {e}")
            return None

    @staticmethod
    def load_latest_model() -> Optional[StopOddsModeler]:
        """Load the most recent traditional model (fallback)"""
        try:
            # Find the latest model file
            model_files = glob.glob("/tmp/stopodds_model_*.lgb")
            if not model_files:
                return None

            # Get the most recent model
            latest_model = max(model_files, key=os.path.getctime)

            # Check if we need to reload (cache for 1 hour)
            model_time = os.path.getctime(latest_model)
            if (PredictionService._cached_model is None or
                PredictionService._model_timestamp is None or
                model_time > PredictionService._model_timestamp):

                modeler = StopOddsModeler()
                modeler.load_model(latest_model)

                PredictionService._cached_model = modeler
                PredictionService._model_timestamp = model_time

            return PredictionService._cached_model

        except Exception as e:
            print(f"Error loading traditional model: {e}")
            return None
    
    @staticmethod
    def prepare_prediction_features(traits: Dict[str, Any]) -> pd.DataFrame:
        """Prepare features for prediction"""
        # Create a single-row DataFrame with the user's traits
        data = {
            'age_bracket': traits.get('age_bracket'),
            'gender': traits.get('gender'),
            'ethnicity': traits.get('ethnicity'),
            'skin_tone': traits.get('skin_tone'),
            'height_bracket': traits.get('height_bracket'),
            'visible_disability': traits.get('visible_disability'),
            'concession': traits.get('concession')
        }
        
        df = pd.DataFrame([data])
        
        # Apply the same preprocessing as in training
        modeler = StopOddsModeler()
        df_processed = modeler.prepare_features(df, for_lgb=True)
        
        # Remove any extra columns that might have been added
        feature_cols = [col for col in df_processed.columns 
                       if col not in ['stops', 'trips', 'id', 'created_at', 'user_agent_hash']]
        
        return df_processed[feature_cols]
    
    @staticmethod
    async def get_personal_estimate(
        db: AsyncSession,
        traits: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get personal risk estimate using adaptive ML models"""

        # Try adaptive ML model first
        adaptive_model = PredictionService.load_latest_adaptive_model()

        if adaptive_model is not None:
            try:
                # Prepare prediction data
                data = {
                    'age_bracket': traits.get('age_bracket'),
                    'gender': traits.get('gender'),
                    'ethnicity': traits.get('ethnicity'),
                    'skin_tone': traits.get('skin_tone'),
                    'height_bracket': traits.get('height_bracket'),
                    'visible_disability': traits.get('visible_disability'),
                    'concession': traits.get('concession'),
                    'trips': 30,  # Default exposure for prediction
                    'stops': 0   # Dummy value for feature engineering
                }

                X_pred = pd.DataFrame([data])

                # Make prediction (returns stops per 30 trips)
                prediction = adaptive_model.predict(X_pred, exposure_new=np.array([30]))[0]

                # Convert to rate per 100 trips
                rate_prediction = (prediction / 30) * 100

                # Simple confidence interval (could be improved with bootstrap)
                ci_lower = max(0.1, rate_prediction * 0.7)
                ci_upper = min(25.0, rate_prediction * 1.4)

                # Get feature importance for explanation
                feature_importance = adaptive_model.get_feature_importance()

                # Generate explanation based on model type and features
                explanations = [
                    f"Prediction from {adaptive_model.model_type} ML model",
                    f"Based on {adaptive_model.sample_size} training samples"
                ]

                if feature_importance is not None and len(feature_importance) > 0:
                    top_feature = feature_importance.iloc[0]['feature']
                    explanations.append(f"Most important factor: {top_feature}")

                # Get model metadata
                latest_model_run = await ModelService.get_latest_model_run(db)
                model_run_id = str(latest_model_run.run_id) if latest_model_run else 'adaptive_ml_latest'

                return {
                    'probability': round(max(0.1, min(rate_prediction, 25.0)), 1),
                    'confidence_interval': [round(ci_lower, 1), round(ci_upper, 1)],
                    'model_run_id': model_run_id,
                    'explanation': explanations,
                    'is_baseline': False,
                    'model_type': adaptive_model.model_type
                }

            except Exception as e:
                print(f"Error in adaptive ML prediction: {e}")
                # Fall through to traditional model

        # Fallback to traditional model
        model = PredictionService.load_latest_model()

        if model is None:
            # Final fallback to baseline
            latest_model_run = await ModelService.get_latest_model_run(db)
            if not latest_model_run:
                return PredictionService.calculate_baseline_estimate(traits)
            else:
                # Enhanced baseline with model metadata
                baseline = PredictionService.calculate_baseline_estimate(traits)
                baseline['model_run_id'] = str(latest_model_run.run_id)
                baseline['explanation'].append("Using statistical baseline from trained model")
                return baseline
        
        try:
            # Prepare features for prediction
            X = PredictionService.prepare_prediction_features(traits)
            
            # Make prediction with uncertainty
            pred_result = model.predict_with_uncertainty(X)
            
            # Convert rate to percentage (per 100 trips)
            rate_prediction = pred_result['prediction'][0] * 100
            ci_lower = pred_result['lower_ci'][0] * 100
            ci_upper = pred_result['upper_ci'][0] * 100
            
            # Cap at reasonable bounds
            rate_prediction = max(0.5, min(rate_prediction, 25.0))
            ci_lower = max(0.1, min(ci_lower, rate_prediction))
            ci_upper = max(rate_prediction, min(ci_upper, 30.0))
            
            # Generate SHAP-based explanations
            explanations = model.explain_prediction(X, max_features=3)
            
            # Get model metadata
            latest_model_run = await ModelService.get_latest_model_run(db)
            model_run_id = str(latest_model_run.run_id) if latest_model_run else 'lightgbm_latest'
            
            return {
                'probability': round(rate_prediction, 1),
                'confidence_interval': [round(ci_lower, 1), round(ci_upper, 1)],
                'model_run_id': model_run_id,
                'explanation': explanations[0].split('; ') if explanations else [
                    "Your profile suggests typical inspection patterns",
                    "Based on machine learning analysis of demographic data"
                ],
                'is_baseline': False
            }
            
        except Exception as e:
            print(f"Error in model prediction: {e}")
            # Fallback to baseline if prediction fails
            return PredictionService.calculate_baseline_estimate(traits)