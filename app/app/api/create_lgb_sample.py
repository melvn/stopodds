"""
Create larger sample dataset for LightGBM testing
"""

import asyncio
import random
import numpy as np
from database import AsyncSessionLocal
from sqlalchemy import text

async def create_lgb_sample_data():
    """Create 400 sample submissions for LightGBM testing"""
    print("Creating LightGBM sample data...")
    
    async with AsyncSessionLocal() as db:
        # Clear existing data (respecting foreign key constraints)
        await db.execute(text("DELETE FROM aggregates_public"))
        await db.execute(text("DELETE FROM model_runs"))
        await db.execute(text("DELETE FROM submissions"))
        await db.commit()
        
        # Create 400 sample submissions
        for i in range(400):
            trips = random.randint(5, 80)
            
            # Create some realistic patterns
            age_bracket = random.choice(['18-24', '25-34', '35-44', '45+', None])
            gender = random.choice(['Male', 'Female', 'Nonbinary', 'PreferNot', None])
            ethnicity = random.choice([
                'Anglo Australian', 'South Asian', 'East Asian', 'European', 
                'Middle Eastern', 'Indigenous', 'African', 'Other', None
            ])
            skin_tone = random.choice(['Light', 'Medium', 'Dark', 'PreferNot', None])
            height_bracket = random.choice(['<160', '160-175', '175-190', '>190', None])
            visible_disability = random.choice([True, False, None]) if random.random() > 0.8 else False
            concession = random.choice([True, False, None])
            
            # Create stop patterns with some demographic bias
            base_rate = 0.08  # Base 8% chance per trip
            
            # Add demographic modifiers to create patterns
            if age_bracket == '18-24':
                base_rate *= 1.3  # Young adults stopped more
            elif age_bracket == '45+':
                base_rate *= 0.8  # Older adults stopped less
                
            if ethnicity in ['South Asian', 'Middle Eastern', 'African']:
                base_rate *= 1.4  # Some ethnic groups stopped more
            elif ethnicity == 'Anglo Australian':
                base_rate *= 0.9  # Reference group
                
            if visible_disability:
                base_rate *= 0.7  # Visible disability may reduce stops
                
            if concession:
                base_rate *= 0.85  # Concession users checked less
            
            # Generate stops using Poisson distribution
            expected_stops = trips * base_rate
            stops = max(0, min(trips, int(np.random.poisson(expected_stops))))
            
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
                'user_agent_hash': f'lgb_sample_{i}'
            })
        
        await db.commit()
        print(f"Created 400 sample submissions!")
        
        # Check stats
        stats_result = await db.execute(text("""
            SELECT COUNT(*) as submissions, SUM(trips) as trips, SUM(stops) as stops 
            FROM submissions
        """))
        stats = stats_result.fetchone()
        
        print(f"Total submissions: {stats.submissions}")
        print(f"Total trips: {stats.trips}")
        print(f"Total stops: {stats.stops}")
        print(f"Overall stop rate: {stats.stops/stats.trips*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(create_lgb_sample_data())