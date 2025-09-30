# StopOdds

Statistical analysis of Melbourne public transport fare inspections. Collects anonymous commuter data to estimate stop rates by demographic group.

## What it does

Submit your trips and stops from the last 30 days with optional demographic info. Get back:
- Stop rates per 100 trips by group
- Personal risk estimates 
- Statistical confidence intervals

## Tech Stack

- **Frontend**: Next.js + TypeScript + Material-UI
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL 
- **Stats**: Poisson/Negative Binomial GLM

## Development

**Backend:**
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd app
npm install
npm run dev
```

**Database:**
Set up PostgreSQL and run `infra/supabase.sql`

## Privacy

- No personal identifiers collected
- Groups under 50 people suppressed
- 12-month data retention max
- Full methodology transparency

## API

- `POST /api/submit` - Submit data
- `GET /api/overview` - Get statistics  
- `GET /api/predict` - Personal estimate
- `GET /api/methods` - Methodology

Public interest project - not gambling related.
