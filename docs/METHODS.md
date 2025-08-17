# StopOdds Methodology

## Statistical Approach

### Primary Model: Poisson Regression with Exposure

We model stop counts using a Poisson regression with an exposure offset:

```
S_i ~ Poisson(λ_i × N_i)
log(λ_i) = β₀ + β_race + β_skin + β_gender + β_height + β_age + β_disability + β_concession
```

Where:
- `S_i` = number of stops for person i
- `N_i` = number of trips for person i (exposure)
- `λ_i` = stop rate per trip for person i

### Overdispersion Check

If Pearson deviance / degrees of freedom > 1.5, we automatically switch to a **Negative Binomial** model to account for overdispersion.

### Incidence Rate Ratios (IRR)

Coefficients are exponentiated to give IRRs: `IRR = exp(β)`

- IRR = 1: no effect
- IRR > 1: increased risk
- IRR < 1: decreased risk

### Confidence Intervals

We report 95% confidence intervals for all IRRs using:
```
CI = exp(β ± 1.96 × SE(β))
```

## Optional: LightGBM Classifier

For enhanced user engagement, we may fit a LightGBM classifier:
- **Target**: Binary (stopped ≥ 1 vs 0)
- **Interpretability**: SHAP values for local explanations
- **Calibration**: Isotonic calibration for probability estimates

## Privacy Protection

### k-Anonymity
- Suppress any group with < 50 respondents
- No cross-tabulations that break k-anonymity
- Aggregate statistics only

### Data Retention
- Raw data: 12 months maximum
- Aggregated data: retained indefinitely
- No personally identifiable information

## Model Validation

### Minimum Sample Requirements
- ≥ 500 total submissions
- ≥ 100 total stops across all submissions

### Robustness Checks
1. **Model Agreement**: Poisson vs Negative Binomial IRR comparison
2. **Perturbation Test**: ±10% noise on trips/stops, check IRR stability
3. **Stratified Analysis**: IRR consistency within concession strata

### Performance Metrics
- **GLM**: Deviance, AIC, BIC, overdispersion ratio
- **LightGBM**: AUC, Brier score, calibration plot

## Limitations and Caveats

1. **Selection Bias**: Self-reported data may not represent all commuters
2. **Recall Bias**: 30-day recall may be imperfect
3. **Small Sample**: Some demographic groups may have limited representation
4. **Temporal Effects**: Stop rates may vary by time/season (not captured)

## Technical Implementation

### Feature Engineering
- Categorical variables → dummy encoding
- Reference categories: first alphabetically
- Missing values → separate "Unknown" category

### Model Training
- Automatic overdispersion detection
- Class weighting for imbalanced data (LightGBM)
- Cross-validation for hyperparameter tuning

### Quality Assurance
- Range validation (trips: 1-200, stops: 0-trips)
- Anomaly detection for extreme values
- Daily hash rotation for fraud detection

## Reporting Standards

All public results include:
- Point estimates with 95% CIs
- Sample sizes (when ≥ 50)
- Model type and training date
- Uncertainty quantification
- Link to this methodology