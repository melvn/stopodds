"""
Quick sample data script using raw SQL to avoid enum issues
"""

import asyncio
import random
import numpy as np
from database import AsyncSessionLocal
from sqlalchemy import text

async def create_quick_sample_data():
    """Create sample data using raw SQL"""
    print("Creating quick sample data...")
    
    async with AsyncSessionLocal() as db:
        # Create 20 sample submissions using raw SQL
        for i in range(20):
            trips = random.randint(5, 50)
            stops = max(0, min(trips, int(np.random.poisson(trips * 0.08))))
            
            age_bracket = random.choice(['18-24', '25-34', '35-44', '45+', None])
            gender = random.choice(['Male', 'Female', 'Nonbinary', 'PreferNot', None])
            ethnicity = random.choice([
                'Anglo Australian', 'South Asian', 'East Asian', 'European', 
                'Middle Eastern', 'Indigenous', None
            ])
            skin_tone = random.choice(['Light', 'Medium', 'Dark', 'PreferNot', None])
            height_bracket = random.choice(['<160', '160-175', '175-190', '>190', None])
            visible_disability = random.choice([True, False, None])
            concession = random.choice([True, False, None])
            
            await db.execute(text("""
                INSERT INTO submissions (age_bracket, gender, ethnicity, skin_tone, height_bracket, 
                                       visible_disability, concession, trips, stops, user_agent_hash)
                VALUES (:age_bracket, :gender, :ethnicity, :skin_tone, :height_bracket,
                        :visible_disability, :concession, :trips, :stops, :user_agent_hash)
            """), {
                'age_bracket': age_bracket,
                'gender': gender, 
                'ethnicity': ethnicity,
                'skin_tone': skin_tone,
                'height_bracket': height_bracket,
                'visible_disability': visible_disability,
                'concession': concession,
                'trips': trips,
                'stops': stops,
                'user_agent_hash': f'quick_sample_{i}'
            })
        
        await db.commit()
        print("Created 20 sample submissions!")
        
        # Create a sample model run
        await db.execute(text("""
            INSERT INTO model_runs (model_type, train_rows, metrics, coeffs, public_snapshot, notes)
            VALUES ('poisson', 20, :metrics, :coeffs, true, 'Quick sample model')
        """), {
            'metrics': '{"deviance": 45.2, "aic": 52.1, "sample_size": 20}',
            'coeffs': '{"intercept": {"coefficient": -2.5, "irr": 0.08}}'
        })
        
        model_result = await db.execute(text("SELECT run_id FROM model_runs ORDER BY created_at DESC LIMIT 1"))
        model_run_id = model_result.scalar()
        
        # Create some sample aggregates
        aggregates = [
            ('age_bracket=18-24', 60, 1200, 150, 12.5),
            ('age_bracket=25-34', 80, 1800, 120, 6.7),
            ('ethnicity=South Asian', 55, 800, 120, 15.0),
            ('ethnicity=Anglo Australian', 75, 2000, 80, 4.0),
        ]
        
        for group_key, n_people, n_trips, n_stops, rate in aggregates:
            if n_people >= 50:  # k-anonymity requirement
                await db.execute(text("""
                    INSERT INTO aggregates_public (group_key, n_people, n_trips, n_stops, 
                                                  rate_per_100, model_run_id)
                    VALUES (:group_key, :n_people, :n_trips, :n_stops, :rate_per_100, :model_run_id)
                """), {
                    'group_key': group_key,
                    'n_people': n_people,
                    'n_trips': n_trips,
                    'n_stops': n_stops,
                    'rate_per_100': rate,
                    'model_run_id': model_run_id
                })
        
        await db.commit()
        print("Created sample model run and aggregates!")
        print("Quick sample data generation complete!")

if __name__ == "__main__":
    asyncio.run(create_quick_sample_data())