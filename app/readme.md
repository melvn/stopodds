# StopOdds

> *"Estimate your chances of being stopped on Melbourne public transport — from commuter-reported data."*

A transparent, privacy-first web application for understanding fare inspection patterns on Melbourne public transport.

**Domain:** `stopodds.com.au`  
**Scope:** Public-interest, non-profit, privacy-first project

## 🎯 Purpose

StopOdds collects anonymous trip and stop counts from commuters to:
- Calculate **stop rates per 100 trips** by demographic group
- Report **Incidence Rate Ratios (IRR)** with confidence intervals
- Provide **personal risk estimates** based on submitted traits
- Maintain full **transparency** in methodology and results

## 🏗️ Architecture

- **Frontend**: Next.js (React) on Vercel
- **API**: FastAPI (Python) on Fly.io/Railway
- **Database**: PostgreSQL (Supabase)
- **Modeling**: Poisson/Negative Binomial GLM, optional LightGBM + SHAP
- **CDN**: Cloudflare

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Docker (optional)

### Development Setup

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd stopodds
   ```

2. **Backend setup**:
   ```bash
   cd api
   cp .env.example .env
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Frontend setup**:
   ```bash
   cd app
   npm install
   npm run dev
   ```

4. **Database setup**:
   - Create PostgreSQL database
   - Run `infra/supabase.sql` schema
   - Update DATABASE_URL in `.env`

### Docker Development
```bash
cd infra
docker-compose up
```

## 📊 Data Model

### Submissions Table
```sql
CREATE TABLE submissions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    age_bracket ENUM,           -- '18-24', '25-34', '35-44', '45+'
    gender ENUM,                -- 'Male', 'Female', 'Nonbinary', 'PreferNot'
    ethnicity ENUM,             -- AUS-relevant categories
    skin_tone ENUM,             -- 'Light', 'Medium', 'Dark', 'PreferNot'
    height_bracket ENUM,        -- '<160', '160-175', '175-190', '>190'
    visible_disability BOOLEAN,
    concession BOOLEAN,         -- Concession/MIPE status
    trips INTEGER,              -- 1-200 trips in last 30 days
    stops INTEGER,              -- 0-trips stops in last 30 days
    user_agent_hash TEXT        -- Daily-salted hash for fraud detection
);
```

## 🔒 Privacy & Security

- **k-anonymity**: Groups <50 people suppressed
- **No identifiers**: No names, emails, IPs, GPS
- **Data retention**: 12 months max for raw data
- **Open methodology**: Full transparency in analysis
- **Australian Privacy Principles** compliant

## 📈 Statistical Methods

### Primary: Poisson GLM
```
S_i ~ Poisson(λ_i × N_i)
log(λ_i) = β₀ + β_race + β_skin + β_gender + β_height + β_age + β_disability + β_concession
```

- **Overdispersion check**: Switch to Negative Binomial if needed
- **Outputs**: IRR = exp(β) with 95% CIs

### Optional: LightGBM + SHAP
- Binary classifier for enhanced engagement
- SHAP explanations for interpretability
- Isotonic calibration for probability estimates

## 🛠️ Development

### API Endpoints
- `POST /api/submit` - Submit trip/stop data
- `GET /api/overview` - Get aggregated statistics
- `GET /api/predict` - Get personal risk estimate
- `GET /api/methods` - Get methodology info

### Testing
```bash
# Backend
cd api
pytest

# Frontend
cd app
npm run test
npm run lint
npm run type-check
```

### Building
```bash
# API Docker image
docker build -f infra/Dockerfile.api -t stopodds-api .

# Frontend build
cd app
npm run build
```

## 🚢 Deployment

### Fly.io (API)
```bash
fly auth login
fly deploy --config infra/fly.toml
```

### Vercel (Frontend)
```bash
vercel --prod
```

### Supabase (Database)
1. Create new project
2. Run SQL from `infra/supabase.sql`
3. Configure connection string

## 📋 Roadmap

- **v0.1**: Form + DB + basic Poisson GLM
- **v1.0**: Public charts, IRR display, personal estimates
- **v1.1**: Negative Binomial auto-switch
- **v1.2**: LightGBM + SHAP explanations
- **v1.3**: Randomized response for sensitive fields

## 🤝 Contributing

1. Read `docs/METHODS.md` for statistical approach
2. Review `docs/PRIVACY.md` for data handling
3. Follow existing code conventions
4. Add tests for new features
5. Ensure k-anonymity compliance

## 📄 License

[License Type] - See LICENSE file

## 🆘 Support

- **Issues**: GitHub Issues
- **Privacy**: privacy@stopodds.com.au
- **General**: info@stopodds.com.au

---

**Disclaimer**: StopOdds is a public-interest statistics project about fare inspections. It is not gambling-related despite the name.

---

## Original Design Document

---

## 0. Principles

* **Minimal data, maximal clarity.** Count stops, not stories. Traits only, no identifiers.
* **First-principles stats first.** Rate models with exposure offsets; show intervals, not hype.
* **Explainability over black boxes.** Boosted trees are allowed only with SHAP; otherwise GLM/NB.
* **Open methods.** Publish methodology, aggregated tables, and code. No raw row-level data release.
* **Local, lawful, ethical.** Comply with Australian Privacy Principles (APP). No re-identification risk.

---

## 1. Product

### 1.1 What users can do

* **Contribute**: Submit last-30-day counts: total trips **N**, times stopped **S**, and fixed traits (age bracket, gender, race/ethnicity, skin tone, height bracket, visible disability, concession/MIPE Y/N).
* **See the science**: Aggregated charts: stop **rate per 100 trips** by group, **Incidence Rate Ratios (IRR)** with CIs, and model notes.
* **Get a personal estimate**: Input traits → receive calibrated probability and short SHAP-style explanation (if boosted model enabled).

### 1.2 What we will **not** do

* No station/time tracking, no location history, no free text, no identifiers, no cookies that track identity, no ads, no sale of data.

---

## 2. Architecture (cost-efficient, functional, modern)

**Front-end:** Next.js (React) on Vercel
**API:** FastAPI (Python) on Fly.io/Railway
**Modeling:** Python (scikit-learn, statsmodels, LightGBM, shap)
**DB:** Postgres (Supabase)
**Storage/Jobs:** Supabase cron / Railway cron or GitHub Actions
**Edge:** Cloudflare (DNS, basic WAF, caching)
**Analytics:** Umami (self-host) or PostHog (self-host), event-level only, no PII
**Error tracking:** Sentry (frontend + backend)
**Auth:** None for survey; admin via GitHub OAuth + IP allowlist

**Why this stack**

* Free/low-cost tiers, fast global CDN, serverless for the UI, simple containers for API, managed Postgres.
* Python keeps the stats/ML clean; Next.js keeps the UI simple and SEO-friendly.

---

## 3. Data model

### 3.1 Table: `submissions`

```
id (uuid)                PK
created_at (timestamptz) default now()
age_bracket (enum)       {18–24, 25–34, 35–44, 45+}
gender (enum)            {Male, Female, Nonbinary, PreferNot}
ethnicity (enum)         {pre-binned AUS-relevant groups}
skin_tone (enum)         {Light, Medium, Dark, PreferNot}
height_bracket (enum)    {<160, 160–175, 175–190, >190}
visible_disability (bool|null)
concession (bool|null)   concession/MIPE indicator
trips (int)              N in last 30 days  (>=1, <=200)
stops (int)              S in last 30 days  (>=0, <=trips)
user_agent_hash (text)   salted hash; optional fraud signal
```

### 3.2 Table: `model_runs`

```
run_id (uuid)            PK
created_at (timestamptz)
model_type (text)        {"poisson","negbin","lightgbm"}
train_rows (int)
metrics (jsonb)          {auc, brier, calibration, deviance}
coeffs (jsonb)           for GLM: betas + CIs; for GBT: feature_importances
public_snapshot (bool)
notes (text)
```

### 3.3 Table: `aggregates_public`

Precomputed public-safe rollups (k≥50 per cell):

```
group_key (text)         e.g., "ethnicity=South Asian"
n_people (int)
n_trips (int)
n_stops (int)
rate_per_100 (float)
irr_vs_ref (float)       with 95% CI
model_run_id (uuid)
```

---

## 4. Modeling

### 4.1 Primary (first-principles)

* **Poisson GLM with exposure**:
  $S_i \sim \text{Poisson}(\lambda_i \cdot N_i)$,
  $\log \lambda_i = \beta_0 + \beta_{race} + \beta_{skin} + \beta_{gender} + \beta_{height} + \beta_{age} + \beta_{disab} + \beta_{concession}$
* **Overdispersion check**: Pearson deviance / df > 1.5 ⇒ switch to **Negative Binomial**.
* **Outputs**: IRR = $e^\beta$, 95% CIs, p-values. Model deviance and goodness-of-fit displayed.

### 4.2 Optional (more engaging, still explainable)

* **LightGBM** classifier (target: stopped≥1 vs 0), with class weights.
* **Interpretability**: SHAP global summary + local explanation for submitted profile.
* **Calibration**: isotonic calibration; show calibration plot.

### 4.3 Minimum sample policy

* Enable model only after **≥500** valid submissions and **≥100** total stops.
* Hide any group cell with **k < 50** respondents (suppression for privacy + stability).

### 4.4 Robustness displays (concise)

* **NB vs Poisson** agreement badge.
* **Perturbation**: ±10% on trips/stops; IRRs stable? badge on/off.
* **Stratified check**: IRR consistency within concession strata.

---

## 5. API (public + internal)

### 5.1 Public endpoints

* `POST /api/submit` → { status }
  Validates enums and ranges, stores row, returns 202.
* `GET /api/overview` → aggregates for charts
  Returns: rates per 100 by group with 95% CIs (k-suppressed).
* `GET /api/predict?traits=...` → personal estimate
  Returns: probability, model\_run\_id, brief explanation (top 3 factors).
* `GET /api/methods` → JSON of current methodology snapshot (model type, last run, thresholds).

### 5.2 Admin endpoints (protected)

* `POST /admin/model/train` → triggers retrain job
* `POST /admin/aggregates/build` → publishes k-safe aggregates
* `GET /admin/health` → DB/queue/model statuses

---

## 6. UX flows

### 6.1 Contribute

* Consent modal (30 words, plain English).
* 1-page form (8 fields + N/S). All optional except N/S. Real-time validation.
* Submit → thanks screen with “what we collect/why” and a link to results.

### 6.2 Results

* **Figure A:** Stop **rate per 100 trips** by group (bars + 95% CI).
* **Figure B:** **IRR vs reference** (log scale dots + CI).
* **Personal card:** “Based on X submissions like yours, estimated probability is p%, (CI a–b%).” + one-liner about uncertainty.
* **Methods accordion:** short, exact, math included.

Accessibility: WCAG AA, keyboard navigation, high-contrast mode.

---

## 7. Privacy & safety

* **Data minimisation:** no names, emails, IPs, GPS, referrers stripped; UA hashed with daily salt; rate-limit via Cloudflare Turnstile/hCaptcha.
* **k-anonymity:** suppress cells with k<50; no cross-tabs exposed that break k.
* **Retention:** raw table retained 12 months; then traits-only retained, with S/N aggregated.
* **Open data:** only publish aggregates meeting privacy thresholds.
* **Compliance:** APP 1–5 (open/transparent mgmt, anonymity, data quality, security), simple DPIA on repo.

---

## 8. Ops & governance

* **CI/CD:** GitHub Actions (type-checks, tests, container build, deploy to Fly.io/Vercel).
* **Monitoring:** Sentry alerts; healthchecks; uptime on BetterStack.
* **Backups:** Daily Postgres snapshot (7-day window).
* **Abuse mitigation:** flood control; anomaly rules (e.g., 200 trips, 200 stops) flagged and excluded.
* **Versioning:** Each model run is immutable; public page shows `model_run_id` and changelog.

---

## 9. Cost model (AUD/month, typical small scale)

| Item                 | Service         | Est. \$      |
| -------------------- | --------------- | ------------ |
| Frontend hosting     | Vercel (Hobby)  | \$0–\$20     |
| API container        | Fly.io/Railway  | \$0–\$10     |
| Postgres             | Supabase (Lite) | \$0–\$25     |
| Sentry               | Free tier       | \$0          |
| Cloudflare           | Free            | \$0          |
| Umami/PostHog (self) | \$5–\$10 infra  | \$5–\$10     |
| **Total**            |                 | **\$5–\$65** |

Scale: comfortably \<A\$100/mo until tens of thousands of monthly sessions.

---

## 10. Roadmap

**v0.1 (Internal)**

* Form + DB + admin-only aggregates
* Poisson GLM, overdispersion check

**v1.0 (Public Launch)**

* Rates per 100 + IRR charts with CIs
* Personal estimate card
* Methods page + transparency

**v1.1**

* Negative Binomial auto-switch
* Calibration plot for classifier route

**v1.2 (Optional)**

* LightGBM + SHAP explanations
* Nightly retrains, snapshot toggle

**v1.3**

* Randomized-response option for sensitive fields (epsilon-LDP toggle; show trade-off)

---

## 11. Copy blocks (use verbatim if you want)

**Consent (modal):**
“We collect anonymous counts (how many trips you took and how many times you were checked) and optional traits (age bracket, gender, ethnicity, skin tone, height, visible disability, concession). No identifiers are collected. Data is used to estimate stop rates by group. Aggregated results are published; small groups are suppressed to protect privacy.”

**Methods (accordion):**
“We model stop counts $S$ with a Poisson or Negative Binomial regression and an exposure offset for trips $N$. Coefficients are reported as Incidence Rate Ratios (IRR). Overdispersion is tested; if present, a Negative Binomial model is used. We show 95% confidence intervals and suppress any group cell with fewer than 50 respondents.”

**Gambling confusion disclaimer (footer):**
“StopOdds is a public-interest statistics project about fare inspections. It is not gambling-related.”

---

## 12. Risks & mitigations

* **Self-selection bias:** Display caveat and collect concession/control fields; show stability across strata.
* **Small cells/identifiability:** k-suppression, binning, no cross-tabs that pierce k.
* **Data poisoning/trolling:** Range checks, anomaly filters, flood control, periodic audit.
* **Misinterpretation:** Prominent uncertainty bars; methods link on every chart.

---

## 13. Success criteria

* ≥500 valid submissions in first month; ≥100 total stops.
* Stable IRRs across Poisson vs NB; perturbation sensitivity shows <10% swing.
* Calibration (if classifier enabled) Brier < 0.2 and visually acceptable reliability.
* Media/advocacy pickup; constructive feedback from commuters.

---

## 14. Repository layout

```
/app          (Next.js)
  /pages
  /components
  /public
/api          (FastAPI)
  main.py
  models.py
  train.py    (GLM/NB, optional LightGBM)
  shap_utils.py
/infra
  dockerfiles
  fly.toml / railway.json
  supabase.sql
/docs
  StopOdds.md (this file)
  METHODS.md  (math + decisions)
  PRIVACY.md
```

---

**Bottom line:** *StopOdds* is small by design: a lean rate model with robust presentation. It’s defensible, cheap to run, and honest about uncertainty — with the option to add boosted trees + SHAP later for interactivity without sacrificing clarity.
