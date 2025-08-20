"""
Generate sample data for testing StopOdds functionality
Run this script to populate the database with realistic test data
"""

import asyncio
import random
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal, init_db
from models import Submission, ModelRun, AggregatePublic, AgeBracket, Gender, Ethnicity, SkinTone, HeightBracket, ModelType
import uuid

# Sample data distributions based on realistic Melbourne demographics
SAMPLE_DISTRIBUTIONS = {
    'age_bracket': {
        AgeBracket.AGE_18_24: 0.25,
        AgeBracket.AGE_25_34: 0.35,
        AgeBracket.AGE_35_44: 0.25,
        AgeBracket.AGE_45_PLUS: 0.15
    },
    'gender': {
        Gender.MALE: 0.48,
        Gender.FEMALE: 0.48,
        Gender.NONBINARY: 0.02,
        Gender.PREFER_NOT: 0.02
    },
    'ethnicity': {
        Ethnicity.ANGLO_AUSTRALIAN: 0.35,
        Ethnicity.SOUTH_ASIAN: 0.15,
        Ethnicity.EAST_ASIAN: 0.20,
        Ethnicity.SOUTHEAST_ASIAN: 0.10,
        Ethnicity.EUROPEAN: 0.08,
        Ethnicity.MIDDLE_EASTERN: 0.05,
        Ethnicity.AFRICAN: 0.03,
        Ethnicity.INDIGENOUS: 0.02,
        Ethnicity.LATIN_AMERICAN: 0.01,
        Ethnicity.OTHER: 0.01
    },
    'skin_tone': {
        SkinTone.LIGHT: 0.45,
        SkinTone.MEDIUM: 0.35,
        SkinTone.DARK: 0.15,
        SkinTone.PREFER_NOT: 0.05
    },
    'height_bracket': {
        HeightBracket.UNDER_160: 0.20,
        HeightBracket.HEIGHT_160_175: 0.50,
        HeightBracket.HEIGHT_175_190: 0.25,
        HeightBracket.OVER_190: 0.05
    },
    'visible_disability': {
        True: 0.08,
        False: 0.87,
        None: 0.05
    },
    'concession': {
        True: 0.35,
        False: 0.60,
        None: 0.05
    }
}

def weighted_choice(choices):
    """Select a random choice based on weights"""
    if isinstance(choices, dict):
        items, weights = zip(*choices.items())
        return random.choices(items, weights=weights, k=1)[0]
    return random.choice(choices)

def generate_submission_data():
    """Generate a realistic submission"""
    # Basic trip data with some correlation to demographics
    trips = random.randint(5, 50)  # Most people take 5-50 trips per month
    
    # Generate demographic data
    age_bracket = weighted_choice(SAMPLE_DISTRIBUTIONS['age_bracket'])
    gender = weighted_choice(SAMPLE_DISTRIBUTIONS['gender'])
    ethnicity = weighted_choice(SAMPLE_DISTRIBUTIONS['ethnicity'])
    skin_tone = weighted_choice(SAMPLE_DISTRIBUTIONS['skin_tone'])
    height_bracket = weighted_choice(SAMPLE_DISTRIBUTIONS['height_bracket'])
    visible_disability = weighted_choice(SAMPLE_DISTRIBUTIONS['visible_disability'])
    concession = weighted_choice(SAMPLE_DISTRIBUTIONS['concession'])
    
    # Calculate stops with some bias based on demographics
    # This simulates real-world patterns where some groups may be checked more/less
    base_stop_rate = 0.08  # 8% base rate
    
    # Apply demographic adjustments (simplified model)
    adjustments = 1.0
    
    if ethnicity in [Ethnicity.SOUTH_ASIAN, Ethnicity.MIDDLE_EASTERN, Ethnicity.AFRICAN]:
        adjustments *= 1.3  # Higher inspection rates
    elif ethnicity in [Ethnicity.ANGLO_AUSTRALIAN, Ethnicity.EUROPEAN]:
        adjustments *= 0.9   # Lower inspection rates
    
    if age_bracket == AgeBracket.AGE_18_24:
        adjustments *= 1.2   # Young adults checked more
    elif age_bracket == AgeBracket.AGE_45_PLUS:
        adjustments *= 0.8   # Older adults checked less
    
    if concession:
        adjustments *= 0.7   # Concession holders checked less
    
    if visible_disability:
        adjustments *= 0.6   # People with disabilities checked less
    
    # Calculate expected stops
    expected_stops = trips * base_stop_rate * adjustments
    
    # Add some randomness using numpy's poisson
    stops = max(0, min(trips, int(np.random.poisson(expected_stops))))
    
    return {
        'age_bracket': age_bracket if random.random() > 0.1 else None,
        'gender': gender if random.random() > 0.05 else None,
        'ethnicity': ethnicity if random.random() > 0.15 else None,
        'skin_tone': skin_tone if random.random() > 0.2 else None,
        'height_bracket': height_bracket if random.random() > 0.25 else None,
        'visible_disability': visible_disability,
        'concession': concession,
        'trips': trips,
        'stops': stops,
        'user_agent_hash': f"sample_hash_{random.randint(1000, 9999)}"
    }

async def create_sample_submissions(db: AsyncSession, count: int = 750):
    """Create sample submissions"""
    print(f"Creating {count} sample submissions...")
    
    submissions = []
    for i in range(count):
        submission_data = generate_submission_data()
        submission = Submission(**submission_data)
        submissions.append(submission)
        
        if i % 100 == 0:
            print(f"Generated {i} submissions...")
    
    db.add_all(submissions)
    await db.commit()
    print(f"Created {count} sample submissions successfully!")

async def create_sample_aggregates(db: AsyncSession, model_run_id: str):
    """Create sample public aggregates"""
    print("Creating sample aggregates...")
    
    # Sample aggregates by different demographic groups
    sample_aggregates = [
        {
            'group_key': 'age_bracket=18-24',
            'n_people': 150,
            'n_trips': 2800,
            'n_stops': 280,
            'rate_per_100': 10.0,
            'irr_vs_ref': 1.25,
            'ci_lower': 1.05,
            'ci_upper': 1.48
        },
        {
            'group_key': 'age_bracket=25-34',
            'n_people': 200,
            'n_trips': 4200,
            'n_stops': 350,
            'rate_per_100': 8.3,
            'irr_vs_ref': 1.04,
            'ci_lower': 0.89,
            'ci_upper': 1.21
        },
        {
            'group_key': 'age_bracket=35-44',
            'n_people': 180,
            'n_trips': 3800,
            'n_stops': 285,
            'rate_per_100': 7.5,
            'irr_vs_ref': 0.94,
            'ci_lower': 0.79,
            'ci_upper': 1.11
        },
        {
            'group_key': 'age_bracket=45+',
            'n_people': 120,
            'n_trips': 2200,
            'n_stops': 140,
            'rate_per_100': 6.4,
            'irr_vs_ref': 0.80,
            'ci_lower': 0.62,
            'ci_upper': 1.02
        },
        {
            'group_key': 'ethnicity=Anglo Australian',
            'n_people': 250,
            'n_trips': 5200,
            'n_stops': 370,
            'rate_per_100': 7.1,
            'irr_vs_ref': 1.00,  # Reference group
            'ci_lower': 0.87,
            'ci_upper': 1.15
        },
        {
            'group_key': 'ethnicity=South Asian',
            'n_people': 120,
            'n_trips': 2500,
            'n_stops': 275,
            'rate_per_100': 11.0,
            'irr_vs_ref': 1.55,
            'ci_lower': 1.28,
            'ci_upper': 1.87
        },
        {
            'group_key': 'ethnicity=East Asian',
            'n_people': 140,
            'n_trips': 2900,
            'n_stops': 240,
            'rate_per_100': 8.3,
            'irr_vs_ref': 1.17,
            'ci_lower': 0.96,
            'ci_upper': 1.42
        },
        {
            'group_key': 'concession=true',
            'n_people': 260,
            'n_trips': 4800,
            'n_stops': 310,
            'rate_per_100': 6.5,
            'irr_vs_ref': 0.78,
            'ci_lower': 0.65,
            'ci_upper': 0.93
        },
        {
            'group_key': 'concession=false',
            'n_people': 420,
            'n_trips': 8500,
            'n_stops': 785,
            'rate_per_100': 9.2,
            'irr_vs_ref': 1.10,
            'ci_lower': 0.98,
            'ci_upper': 1.24
        }
    ]
    
    aggregates = []
    for agg_data in sample_aggregates:
        aggregate = AggregatePublic(
            group_key=agg_data['group_key'],
            n_people=agg_data['n_people'],
            n_trips=agg_data['n_trips'],
            n_stops=agg_data['n_stops'],
            rate_per_100=agg_data['rate_per_100'],
            irr_vs_ref=agg_data['irr_vs_ref'],
            confidence_interval_lower=agg_data['ci_lower'],
            confidence_interval_upper=agg_data['ci_upper'],
            model_run_id=model_run_id
        )
        aggregates.append(aggregate)
    
    db.add_all(aggregates)
    await db.commit()
    print(f"Created {len(aggregates)} sample aggregates!")

async def create_sample_model_run(db: AsyncSession):
    """Create a sample model run"""
    print("Creating sample model run...")
    
    model_run = ModelRun(
        model_type=ModelType.POISSON,
        train_rows=650,
        metrics={
            "deviance": 1247.3,
            "aic": 1283.4,
            "overdispersion": 1.12,
            "sample_size": 650,
            "total_stops": 1055
        },
        coeffs={
            "intercept": {"coefficient": -2.53, "irr": 0.08, "ci_lower": 0.06, "ci_upper": 0.11, "p_value": 0.001},
            "age_18-24": {"coefficient": 0.22, "irr": 1.25, "ci_lower": 1.05, "ci_upper": 1.48, "p_value": 0.012},
            "ethnicity_south_asian": {"coefficient": 0.44, "irr": 1.55, "ci_lower": 1.28, "ci_upper": 1.87, "p_value": 0.001},
            "concession": {"coefficient": -0.25, "irr": 0.78, "ci_lower": 0.65, "ci_upper": 0.93, "p_value": 0.007}
        },
        public_snapshot=True,
        notes="Initial model trained on sample data. Poisson regression with exposure offset."
    )
    
    db.add(model_run)
    await db.commit()
    await db.refresh(model_run)
    
    print(f"Created sample model run: {model_run.run_id}")
    return str(model_run.run_id)

async def generate_all_sample_data():
    """Generate all sample data"""
    print("Initializing database...")
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # Create submissions
        await create_sample_submissions(db, 650)
        
        # Create model run
        model_run_id = await create_sample_model_run(db)
        
        # Create aggregates
        await create_sample_aggregates(db, model_run_id)
        
        print("Sample data generation complete!")
        print("You now have:")
        print("- 650 sample submissions")
        print("- 1 trained model run")
        print("- 9 public aggregates")
        print("\nThe API endpoints should now return meaningful data!")

if __name__ == "__main__":
    asyncio.run(generate_all_sample_data())