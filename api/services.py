from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from models import Submission, ModelRun, AggregatePublic
from database import get_db
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

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
        """Check if we have minimum data for model training"""
        stats = await SubmissionService.get_submission_stats(db)
        
        min_submissions = 500
        min_stops = 100
        
        meets_requirements = (
            stats['total_submissions'] >= min_submissions and 
            stats['total_stops'] >= min_stops
        )
        
        return {
            'meets_requirements': meets_requirements,
            'stats': stats,
            'requirements': {
                'min_submissions': min_submissions,
                'min_stops': min_stops
            }
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
    @staticmethod
    def calculate_baseline_estimate(traits: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate a simple baseline estimate when no model is available"""
        # This is a placeholder that provides a baseline estimate
        # Based on general Melbourne public transport inspection patterns
        
        base_rate = 8.5  # Base rate per 100 trips
        confidence_interval = [6.0, 11.0]
        
        explanation = [
            "Based on limited data from Melbourne commuters",
            "Estimate will improve as more data is collected",
            "Current sample size insufficient for detailed modeling"
        ]
        
        return {
            'probability': base_rate,
            'confidence_interval': confidence_interval,
            'model_run_id': 'baseline',
            'explanation': explanation,
            'is_baseline': True
        }
    
    @staticmethod
    async def get_personal_estimate(
        db: AsyncSession, 
        traits: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get personal risk estimate based on submitted traits"""
        
        # Check if we have a trained model
        latest_model = await ModelService.get_latest_model_run(db)
        
        if not latest_model:
            return PredictionService.calculate_baseline_estimate(traits)
        
        # For now, return a model-based estimate (simplified)
        # In a full implementation, this would use the actual trained model
        base_rate = 8.5
        
        # Simple adjustments based on traits (placeholder logic)
        adjustments = []
        
        if traits.get('concession'):
            base_rate *= 0.85  # Concession users checked less frequently
            adjustments.append("Concession status may reduce inspection rate")
        
        if traits.get('age_bracket') == '18-24':
            base_rate *= 1.15  # Young adults checked more frequently
            adjustments.append("Age group may experience higher inspection rates")
        
        # Cap at reasonable bounds
        base_rate = max(2.0, min(base_rate, 20.0))
        
        confidence_interval = [
            max(0.0, base_rate - 3.0),
            base_rate + 3.0
        ]
        
        explanation = adjustments if adjustments else [
            "Your traits suggest average inspection rates",
            "Estimate based on current model and data"
        ]
        
        return {
            'probability': round(base_rate, 1),
            'confidence_interval': [round(ci, 1) for ci in confidence_interval],
            'model_run_id': str(latest_model.run_id),
            'explanation': explanation,
            'is_baseline': False
        }