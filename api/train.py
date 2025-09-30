import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, roc_auc_score, log_loss
from sklearn.preprocessing import LabelEncoder
import statsmodels.api as sm
from statsmodels.genmod.families import Poisson, NegativeBinomial
import lightgbm as lgb
import shap
from typing import Dict, Any, Optional, Tuple, List
import json
import pickle
import joblib
from datetime import datetime
from scipy import stats
from adaptive_ml import AdaptiveMLPipeline

class StopOddsModeler:
    def __init__(self):
        self.model = None
        self.model_type = None
        self.feature_names = None
        self.shap_explainer = None
        
    def prepare_features(self, df: pd.DataFrame, for_lgb: bool = True) -> pd.DataFrame:
        """Convert categorical variables for modeling"""
        df_prep = df.copy()
        categorical_cols = ['age_bracket', 'gender', 'ethnicity', 'skin_tone', 'height_bracket']
        
        if for_lgb:
            # LightGBM can handle categorical features natively
            # Convert to categorical type and handle nulls
            for col in categorical_cols:
                if col in df_prep.columns:
                    df_prep[col] = df_prep[col].fillna('Unknown').astype('category')
            
            # Convert boolean columns
            for col in ['visible_disability', 'concession']:
                if col in df_prep.columns:
                    df_prep[col] = df_prep[col].fillna(False).astype(int)
                    
            # Create interaction features
            if 'age_bracket' in df_prep.columns and 'gender' in df_prep.columns:
                df_prep['age_gender'] = (df_prep['age_bracket'].astype(str) + '_' + 
                                       df_prep['gender'].astype(str)).astype('category')
            
            return df_prep
        else:
            # Traditional dummy encoding for GLM models
            df_encoded = pd.get_dummies(df_prep, columns=categorical_cols, drop_first=True)
            
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
    
    def fit_lightgbm_model(self, X: pd.DataFrame, y: pd.Series, trips: pd.Series) -> Dict[str, Any]:
        """Fit LightGBM regressor for stop rate prediction"""
        # Create stop rate as target (stops per trip)
        y_rate = y / trips
        
        # Split data
        X_train, X_test, y_train, y_test, trips_train, trips_test = train_test_split(
            X, y_rate, trips, test_size=0.2, random_state=42, stratify=(y > 0).astype(int)
        )
        
        # Identify categorical features
        categorical_features = [i for i, col in enumerate(X.columns) 
                              if X[col].dtype.name == 'category']
        
        # Train LightGBM regressor
        train_data = lgb.Dataset(
            X_train, 
            label=y_train,
            weight=trips_train,  # Weight by number of trips
            categorical_feature=categorical_features
        )
        
        valid_data = lgb.Dataset(
            X_test,
            label=y_test, 
            weight=trips_test,
            categorical_feature=categorical_features,
            reference=train_data
        )
        
        params = {
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'seed': 42
        }
        
        model = lgb.train(
            params,
            train_data,
            valid_sets=[valid_data],
            num_boost_round=300,
            callbacks=[lgb.early_stopping(20), lgb.log_evaluation(0)]
        )
        
        # Predictions and metrics
        y_pred = model.predict(X_test, num_iteration=model.best_iteration)
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred, sample_weight=trips_test))
        mae = np.mean(np.abs(y_test - y_pred))
        
        # R-squared
        ss_res = np.sum((y_test - y_pred) ** 2)
        ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # SHAP values for interpretability
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test[:100])  # Sample for efficiency
        
        # Feature importance
        feature_importance = dict(zip(X.columns, model.feature_importance('gain')))
        
        # Cross-validation for robustness
        cv_scores = []
        for fold in range(3):
            X_cv_train, X_cv_val, y_cv_train, y_cv_val, trips_cv_train, trips_cv_val = train_test_split(
                X_train, y_train, trips_train, test_size=0.2, random_state=fold
            )
            
            cv_train_data = lgb.Dataset(
                X_cv_train, label=y_cv_train, weight=trips_cv_train,
                categorical_feature=categorical_features
            )
            
            cv_model = lgb.train(params, cv_train_data, num_boost_round=model.best_iteration, callbacks=[lgb.log_evaluation(0)])
            cv_pred = cv_model.predict(X_cv_val)
            cv_rmse = np.sqrt(mean_squared_error(y_cv_val, cv_pred, sample_weight=trips_cv_val))
            cv_scores.append(cv_rmse)
        
        metrics = {
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'cv_rmse_mean': float(np.mean(cv_scores)),
            'cv_rmse_std': float(np.std(cv_scores)),
            'best_iteration': int(model.best_iteration),
            'feature_importance': {k: float(v) for k, v in feature_importance.items()}
        }
        
        self.model = model
        self.model_type = 'lightgbm'
        self.feature_names = list(X.columns)
        self.shap_explainer = explainer
        self.categorical_features = categorical_features
        
        return {
            'model_type': 'lightgbm',
            'metrics': metrics,
            'feature_importance': feature_importance
        }
    
    def predict(self, X: pd.DataFrame, trips: Optional[pd.Series] = None) -> np.ndarray:
        """Make predictions with the fitted model"""
        if self.model is None:
            raise ValueError("No model has been fitted")
            
        if self.model_type in ['poisson', 'negbin']:
            X_with_const = sm.add_constant(X)
            if trips is not None:
                return self.model.predict(X_with_const, exposure=trips)
            else:
                return self.model.predict(X_with_const)
        
        elif self.model_type == 'lightgbm':
            # Predict stop rate, then multiply by trips if provided
            rate_pred = self.model.predict(X, num_iteration=self.model.best_iteration)
            if trips is not None:
                return rate_pred * trips
            return rate_pred
        
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def predict_with_uncertainty(self, X: pd.DataFrame, trips: Optional[pd.Series] = None, 
                               n_bootstrap: int = 100) -> Dict[str, np.ndarray]:
        """Make predictions with uncertainty estimates using bootstrap"""
        if self.model_type != 'lightgbm':
            # Fallback to regular prediction for non-LightGBM models
            pred = self.predict(X, trips)
            return {
                'prediction': pred,
                'lower_ci': pred * 0.8,  # Simple fallback
                'upper_ci': pred * 1.2
            }
        
        # Bootstrap predictions for uncertainty
        predictions = []
        for i in range(n_bootstrap):
            # Add small random noise to features to simulate uncertainty
            X_noise = X.copy()
            for col in X.select_dtypes(include=[np.number]).columns:
                noise = np.random.normal(0, 0.01, size=len(X))
                X_noise[col] = X_noise[col] + noise
            
            rate_pred = self.model.predict(X_noise, num_iteration=self.model.best_iteration)
            if trips is not None:
                pred = rate_pred * trips
            else:
                pred = rate_pred
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        return {
            'prediction': np.mean(predictions, axis=0),
            'lower_ci': np.percentile(predictions, 2.5, axis=0),
            'upper_ci': np.percentile(predictions, 97.5, axis=0)
        }
    
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
                # More descriptive explanations
                if abs_impact < 0.001:  # Skip very small impacts
                    continue
                    
                direction = "increases" if impact > 0 else "reduces"
                
                # Clean up feature names for better readability
                clean_name = feature_name.replace('_', ' ').title()
                if 'Gender' in clean_name:
                    clean_name = 'Gender identity'
                elif 'Age' in clean_name:
                    clean_name = 'Age group'
                elif 'Ethnicity' in clean_name:
                    clean_name = 'Ethnic background'
                
                explanation_parts.append(f"{clean_name} {direction} inspection probability")
            
            if not explanation_parts:
                explanations.append("Your profile suggests average inspection rates")
            else:
                explanations.append("; ".join(explanation_parts))
        
        return explanations
    
    def save_model(self, filepath: str):
        """Save the trained model to disk"""
        if self.model is None:
            raise ValueError("No model to save")
        
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'categorical_features': getattr(self, 'categorical_features', None)
        }
        
        if self.model_type == 'lightgbm':
            # Save LightGBM model
            self.model.save_model(f"{filepath}.lgb")
            # Save metadata
            with open(f"{filepath}_meta.pkl", 'wb') as f:
                pickle.dump({
                    'model_type': self.model_type,
                    'feature_names': self.feature_names,
                    'categorical_features': self.categorical_features
                }, f)
        else:
            # Save other models with joblib
            joblib.dump(model_data, f"{filepath}.pkl")
    
    def load_model(self, filepath: str):
        """Load a trained model from disk"""
        if filepath.endswith('.lgb'):
            # Load LightGBM model
            self.model = lgb.Booster(model_file=filepath)
            self.model_type = 'lightgbm'
            
            # Load metadata
            meta_path = filepath.replace('.lgb', '_meta.pkl')
            with open(meta_path, 'rb') as f:
                meta = pickle.load(f)
                self.feature_names = meta['feature_names']
                self.categorical_features = meta['categorical_features']
            
            # Recreate SHAP explainer for LightGBM
            try:
                self.shap_explainer = shap.TreeExplainer(self.model)
            except Exception as e:
                print(f"Could not create SHAP explainer: {e}")
                self.shap_explainer = None
        else:
            # Load other models
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.model_type = model_data['model_type']
            self.feature_names = model_data['feature_names']

def train_models(df: pd.DataFrame, min_sample_size: int = 50, min_stops: int = 10) -> Dict[str, Any]:
    """Adaptive ML training function - scales with sample size"""

    # Adaptive minimum requirements
    sample_size = len(df)
    total_stops = df['stops'].sum()

    print(f"Training with {sample_size} samples, {total_stops} total stops")

    # Very low minimums to allow small dataset training
    if sample_size < min_sample_size:
        raise ValueError(f"Insufficient data: {sample_size} < {min_sample_size}")

    if total_stops < min_stops:
        raise ValueError(f"Insufficient stops: {total_stops} < {min_stops}")

    results = {}

    # Try adaptive ML pipeline first
    try:
        ml_pipeline = AdaptiveMLPipeline()
        ml_results = ml_pipeline.fit(df)

        # Save the trained model
        model_path = f"/tmp/stopodds_adaptive_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        ml_pipeline.save_model(model_path)

        results['adaptive_ml'] = ml_results
        results['primary_model'] = ml_results['model_type']
        results['model_path'] = model_path

        # Get feature importance if available
        feature_importance = ml_pipeline.get_feature_importance()
        if feature_importance is not None:
            results['feature_importance'] = feature_importance.head(10).to_dict('records')

    except Exception as e:
        print(f"Adaptive ML training failed: {str(e)}")
        results['adaptive_ml_error'] = str(e)
        results['primary_model'] = None
    
    # Fallback to traditional GLM if adaptive ML fails
    if 'adaptive_ml_error' in results:
        try:
            # Clean data for GLM (remove rows with None values)
            df_clean = df.dropna(subset=['trips', 'stops'])
            df_clean = df_clean[df_clean['trips'] > 0]
            
            # Reset modeler for GLM
            modeler = StopOddsModeler()
            
            # Prepare features for GLM
            df_glm = modeler.prepare_features(df_clean, for_lgb=False)
            feature_cols_glm = [col for col in df_glm.columns 
                               if col not in ['stops', 'trips', 'id', 'created_at', 'user_agent_hash']]
            
            X_glm = df_glm[feature_cols_glm]
            y = df_glm['stops']
            exposure = df_glm['trips']
            
            # Fit Poisson model
            poisson_results = modeler.fit_poisson_model(X_glm, y, exposure)
            results['poisson'] = poisson_results
            
            # If overdispersion detected, fit Negative Binomial
            if poisson_results['overdispersion_detected']:
                negbin_results = modeler.fit_negbin_model(X_glm, y, exposure)
                results['negbin'] = negbin_results
                results['primary_model'] = 'negbin'
            else:
                results['primary_model'] = 'poisson'
                
        except Exception as e:
            results['glm_error'] = str(e)
            results['primary_model'] = 'baseline'
    
    # Training metadata
    results['training_metadata'] = {
        'timestamp': datetime.now().isoformat(),
        'sample_size': len(df),
        'total_stops': int(df['stops'].sum()),
        'total_trips': int(df['trips'].sum()),
        'stop_rate_mean': float(df['stops'].sum() / df['trips'].sum()),
        'feature_columns': feature_cols_lgb if 'lightgbm' in results else 
                          (feature_cols_glm if 'poisson' in results else []),
        'model_priority': ['lightgbm', 'negbin', 'poisson', 'baseline']
    }
    
    return results