import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, roc_auc_score
import statsmodels.api as sm
from statsmodels.genmod.families import Poisson, NegativeBinomial
import lightgbm as lgb
import shap
from typing import Dict, Any, Optional, Tuple
import json
from datetime import datetime

class StopOddsModeler:
    def __init__(self):
        self.model = None
        self.model_type = None
        self.feature_names = None
        self.shap_explainer = None
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert categorical variables to dummy variables for modeling"""
        categorical_cols = ['age_bracket', 'gender', 'ethnicity', 'skin_tone', 'height_bracket']
        
        # Create dummy variables
        df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        
        # Add boolean columns as integers
        if 'visible_disability' in df.columns:
            df_encoded['visible_disability'] = df['visible_disability'].astype(int)
        if 'concession' in df.columns:
            df_encoded['concession'] = df['concession'].astype(int)
            
        return df_encoded
    
    def fit_poisson_model(self, X: pd.DataFrame, y: pd.Series, exposure: pd.Series) -> Dict[str, Any]:
        """Fit Poisson GLM with exposure offset"""
        # Add constant for intercept
        X_with_const = sm.add_constant(X)
        
        # Fit Poisson model
        model = sm.GLM(y, X_with_const, family=Poisson(), exposure=exposure)
        results = model.fit()
        
        # Check for overdispersion
        pearson_chi2 = results.pearson_chi2
        df_resid = results.df_resid
        overdispersion = pearson_chi2 / df_resid if df_resid > 0 else 0
        
        # Calculate coefficients and confidence intervals
        coeffs = {}
        for i, param in enumerate(results.params.index):
            coeff = results.params[i]
            ci_lower, ci_upper = results.conf_int().iloc[i]
            coeffs[param] = {
                'coefficient': float(coeff),
                'irr': float(np.exp(coeff)),  # Incidence Rate Ratio
                'ci_lower': float(np.exp(ci_lower)),
                'ci_upper': float(np.exp(ci_upper)),
                'p_value': float(results.pvalues[i])
            }
        
        metrics = {
            'deviance': float(results.deviance),
            'pearson_chi2': float(pearson_chi2),
            'overdispersion': float(overdispersion),
            'aic': float(results.aic),
            'bic': float(results.bic)
        }
        
        self.model = results
        self.model_type = 'poisson'
        
        return {
            'model_type': 'poisson',
            'coefficients': coeffs,
            'metrics': metrics,
            'overdispersion_detected': overdispersion > 1.5
        }
    
    def fit_negbin_model(self, X: pd.DataFrame, y: pd.Series, exposure: pd.Series) -> Dict[str, Any]:
        """Fit Negative Binomial GLM with exposure offset"""
        X_with_const = sm.add_constant(X)
        
        # Fit Negative Binomial model
        model = sm.GLM(y, X_with_const, family=NegativeBinomial(), exposure=exposure)
        results = model.fit()
        
        # Calculate coefficients and confidence intervals
        coeffs = {}
        for i, param in enumerate(results.params.index):
            coeff = results.params[i]
            ci_lower, ci_upper = results.conf_int().iloc[i]
            coeffs[param] = {
                'coefficient': float(coeff),
                'irr': float(np.exp(coeff)),
                'ci_lower': float(np.exp(ci_lower)),
                'ci_upper': float(np.exp(ci_upper)),
                'p_value': float(results.pvalues[i])
            }
        
        metrics = {
            'deviance': float(results.deviance),
            'aic': float(results.aic),
            'bic': float(results.bic)
        }
        
        self.model = results
        self.model_type = 'negbin'
        
        return {
            'model_type': 'negbin',
            'coefficients': coeffs,
            'metrics': metrics
        }
    
    def fit_lightgbm_model(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Fit LightGBM classifier for stop/no-stop prediction"""
        # Convert to binary classification problem
        y_binary = (y > 0).astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_binary, test_size=0.2, random_state=42, stratify=y_binary
        )
        
        # Calculate class weights
        pos_weight = (y_binary == 0).sum() / (y_binary == 1).sum()
        
        # Train LightGBM
        train_data = lgb.Dataset(X_train, label=y_train)
        
        params = {
            'objective': 'binary',
            'metric': 'binary_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': 0,
            'scale_pos_weight': pos_weight
        }
        
        model = lgb.train(
            params,
            train_data,
            valid_sets=[train_data],
            num_boost_round=100,
            callbacks=[lgb.early_stopping(10), lgb.log_evaluation(0)]
        )
        
        # Predictions and metrics
        y_pred_proba = model.predict(X_test, num_iteration=model.best_iteration)
        auc = roc_auc_score(y_test, y_pred_proba)
        
        # SHAP values for interpretability
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        
        # Feature importance
        feature_importance = dict(zip(X.columns, model.feature_importance('gain')))
        
        metrics = {
            'auc': float(auc),
            'feature_importance': {k: float(v) for k, v in feature_importance.items()}
        }
        
        self.model = model
        self.model_type = 'lightgbm'
        self.feature_names = list(X.columns)
        self.shap_explainer = explainer
        
        return {
            'model_type': 'lightgbm',
            'metrics': metrics,
            'feature_importance': feature_importance
        }
    
    def predict(self, X: pd.DataFrame, exposure: Optional[pd.Series] = None) -> np.ndarray:
        """Make predictions with the fitted model"""
        if self.model is None:
            raise ValueError("No model has been fitted")
            
        if self.model_type in ['poisson', 'negbin']:
            X_with_const = sm.add_constant(X)
            if exposure is not None:
                return self.model.predict(X_with_const, exposure=exposure)
            else:
                return self.model.predict(X_with_const)
        
        elif self.model_type == 'lightgbm':
            return self.model.predict(X, num_iteration=self.model.best_iteration)
        
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def explain_prediction(self, X: pd.DataFrame, max_features: int = 3) -> List[str]:
        """Generate SHAP-based explanation for LightGBM predictions"""
        if self.model_type != 'lightgbm' or self.shap_explainer is None:
            return ["Explanations only available for LightGBM models"]
        
        shap_values = self.shap_explainer.shap_values(X)
        
        explanations = []
        for i in range(len(X)):
            # Get top contributing features
            feature_impacts = [(abs(shap_values[i][j]), self.feature_names[j], shap_values[i][j]) 
                             for j in range(len(self.feature_names))]
            feature_impacts.sort(reverse=True)
            
            explanation_parts = []
            for abs_impact, feature_name, impact in feature_impacts[:max_features]:
                direction = "increases" if impact > 0 else "decreases"
                explanation_parts.append(f"{feature_name} {direction} risk")
            
            explanations.append("; ".join(explanation_parts))
        
        return explanations

def train_models(df: pd.DataFrame, min_sample_size: int = 500, min_stops: int = 100) -> Dict[str, Any]:
    """Main training function"""
    if len(df) < min_sample_size:
        raise ValueError(f"Insufficient data: {len(df)} < {min_sample_size}")
    
    if df['stops'].sum() < min_stops:
        raise ValueError(f"Insufficient stops: {df['stops'].sum()} < {min_stops}")
    
    modeler = StopOddsModeler()
    
    # Prepare features
    df_encoded = modeler.prepare_features(df)
    
    # Separate features from target and exposure
    feature_cols = [col for col in df_encoded.columns 
                   if col not in ['stops', 'trips', 'id', 'created_at', 'user_agent_hash']]
    
    X = df_encoded[feature_cols]
    y = df_encoded['stops']
    exposure = df_encoded['trips']
    
    results = {}
    
    # Fit Poisson model first
    poisson_results = modeler.fit_poisson_model(X, y, exposure)
    results['poisson'] = poisson_results
    
    # If overdispersion detected, fit Negative Binomial
    if poisson_results['overdispersion_detected']:
        negbin_results = modeler.fit_negbin_model(X, y, exposure)
        results['negbin'] = negbin_results
    
    # Optionally fit LightGBM
    try:
        lgb_results = modeler.fit_lightgbm_model(X, y)
        results['lightgbm'] = lgb_results
    except Exception as e:
        results['lightgbm_error'] = str(e)
    
    results['training_metadata'] = {
        'timestamp': datetime.now().isoformat(),
        'sample_size': len(df),
        'total_stops': int(df['stops'].sum()),
        'total_trips': int(df['trips'].sum()),
        'feature_columns': feature_cols
    }
    
    return results