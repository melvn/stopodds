import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge, Lasso, ElasticNet, PoissonRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, KFold, train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.feature_selection import SelectKBest, f_regression, RFE
# Removed heavy dependencies: xgboost, catboost, optuna
import lightgbm as lgb
import shap
from typing import Dict, Any, Optional, Tuple, List
import joblib
import warnings
warnings.filterwarnings('ignore')

class AdaptiveMLPipeline:
    """
    ML pipeline that adapts model complexity based on sample size

    Sample Size Tiers:
    - < 100: Regularized linear models only
    - 100-300: Single tree models with careful validation
    - 300-1000: Ensemble methods with hyperparameter tuning
    - 1000+: Full ML pipeline with neural networks
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_selector = None
        self.feature_names = None
        self.model_type = None
        self.sample_size = 0
        self.fitted = False

    def get_model_tier(self, n_samples: int) -> str:
        """Determine appropriate model complexity tier"""
        if n_samples < 100:
            return "regularized_linear"
        elif n_samples < 300:
            return "single_tree"
        elif n_samples < 1000:
            return "ensemble"
        else:
            return "full_ml"

    def prepare_features(self, df: pd.DataFrame, create_interactions: bool = True) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """Enhanced feature engineering with automatic interaction detection"""
        df_prep = df.copy()

        # Target and exposure
        y = df_prep['stops']
        exposure = df_prep['trips']

        # Categorical encoding
        categorical_cols = ['age_bracket', 'gender', 'ethnicity', 'skin_tone', 'height_bracket']
        df_encoded = pd.get_dummies(df_prep, columns=categorical_cols, drop_first=True)

        # Boolean columns
        for col in ['visible_disability', 'concession']:
            if col in df_prep.columns:
                df_encoded[col] = df_prep[col].fillna(False).astype(int)

        # Remove target columns
        feature_cols = [col for col in df_encoded.columns
                       if col not in ['stops', 'trips']]
        X = df_encoded[feature_cols]

        # Create interaction features if sufficient data
        if create_interactions and len(df) >= 100:
            # Only create interactions between most important categorical variables
            binary_cols = [col for col in X.columns if X[col].nunique() == 2]

            if len(binary_cols) >= 2:
                # Create pairwise interactions for binary features
                for i in range(len(binary_cols)):
                    for j in range(i+1, min(i+3, len(binary_cols))):  # Limit interactions
                        col1, col2 = binary_cols[i], binary_cols[j]
                        X[f"{col1}_x_{col2}"] = X[col1] * X[col2]

        self.feature_names = X.columns.tolist()
        return X, y, exposure

    def fit_regularized_linear(self, X: pd.DataFrame, y: pd.Series, exposure: pd.Series) -> Dict[str, Any]:
        """Fit regularized linear models for small datasets (< 100 samples)"""
        print(f"Using regularized linear models for {len(X)} samples")

        # Convert to rate for modeling
        y_rate = y / exposure

        # Feature scaling
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Try multiple regularized models with cross-validation
        models = {
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=0.1),
            'elastic_net': ElasticNet(alpha=0.1, l1_ratio=0.5),
            'poisson': PoissonRegressor(alpha=1.0)
        }

        best_score = -np.inf
        best_model = None
        best_name = None

        # 5-fold CV (or leave-one-out if very small)
        cv_folds = min(5, len(X))
        cv = KFold(n_splits=cv_folds, shuffle=True, random_state=42)

        results = {}
        for name, model in models.items():
            try:
                if name == 'poisson':
                    # Poisson regressor needs count data
                    scores = cross_val_score(model, X_scaled, y, cv=cv,
                                           scoring='neg_mean_squared_error')
                else:
                    scores = cross_val_score(model, X_scaled, y_rate, cv=cv,
                                           scoring='neg_mean_squared_error')

                mean_score = np.mean(scores)
                results[name] = {
                    'cv_score': mean_score,
                    'cv_std': np.std(scores)
                }

                if mean_score > best_score:
                    best_score = mean_score
                    best_model = model
                    best_name = name

            except Exception as e:
                print(f"Failed to fit {name}: {e}")
                results[name] = {'error': str(e)}

        # Fit best model
        if best_model is not None:
            if best_name == 'poisson':
                best_model.fit(X_scaled, y)
            else:
                best_model.fit(X_scaled, y_rate)

            self.model = best_model
            self.model_type = f"regularized_{best_name}"
        else:
            raise ValueError("All regularized models failed to fit")

        return {
            'model_type': self.model_type,
            'best_cv_score': best_score,
            'all_results': results,
            'n_features': X.shape[1]
        }

    def fit_single_tree(self, X: pd.DataFrame, y: pd.Series, exposure: pd.Series) -> Dict[str, Any]:
        """Fit single tree models for medium datasets (100-300 samples)"""
        print(f"Using single tree models for {len(X)} samples")

        y_rate = y / exposure
        X_train, X_test, y_train, y_test, exp_train, exp_test = train_test_split(
            X, y_rate, exposure, test_size=0.2, random_state=42
        )

        # Feature scaling
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Feature selection (keep top features)
        max_features = min(10, X.shape[1] // 2)
        self.feature_selector = SelectKBest(f_regression, k=max_features)
        X_train_selected = self.feature_selector.fit_transform(X_train_scaled, y_train)
        X_test_selected = self.feature_selector.transform(X_test_scaled)

        models = {
            'random_forest': RandomForestRegressor(
                n_estimators=50, max_depth=3, random_state=42
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42
            ),
            'lightgbm': lgb.LGBMRegressor(
                n_estimators=50, max_depth=3, learning_rate=0.1,
                random_state=42, verbosity=-1
            )
        }

        best_score = -np.inf
        best_model = None
        best_name = None
        results = {}

        for name, model in models.items():
            try:
                if hasattr(model, 'fit') and 'sample_weight' in model.fit.__code__.co_varnames:
                    model.fit(X_train_selected, y_train, sample_weight=exp_train)
                else:
                    model.fit(X_train_selected, y_train)
                y_pred = model.predict(X_test_selected)

                # Weighted R²
                score = r2_score(y_test, y_pred, sample_weight=exp_test)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred, sample_weight=exp_test))

                results[name] = {
                    'r2_score': score,
                    'rmse': rmse
                }

                if score > best_score:
                    best_score = score
                    best_model = model
                    best_name = name

            except Exception as e:
                print(f"Failed to fit {name}: {e}")
                results[name] = {'error': str(e)}

        if best_model is not None:
            self.model = best_model
            self.model_type = f"tree_{best_name}"
        else:
            raise ValueError("All tree models failed to fit")

        return {
            'model_type': self.model_type,
            'best_r2_score': best_score,
            'n_features_selected': max_features,
            'all_results': results
        }

    def fit_ensemble(self, X: pd.DataFrame, y: pd.Series, exposure: pd.Series) -> Dict[str, Any]:
        """Fit ensemble models using simple grid search (300-1000 samples)"""
        print(f"Using ensemble models for {len(X)} samples")

        y_rate = y / exposure
        X_train, X_test, y_train, y_test, exp_train, exp_test = train_test_split(
            X, y_rate, exposure, test_size=0.2, random_state=42
        )

        # Feature scaling and selection
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Use more features for larger datasets
        max_features = min(20, X.shape[1])
        self.feature_selector = SelectKBest(f_regression, k=max_features)
        X_train_selected = self.feature_selector.fit_transform(X_train_scaled, y_train)
        X_test_selected = self.feature_selector.transform(X_test_scaled)

        # Simple grid search for LightGBM (only model that builds reliably)
        best_score = -np.inf
        best_model = None
        best_params = {}

        param_grid = [
            {'n_estimators': 50, 'max_depth': 3, 'learning_rate': 0.1},
            {'n_estimators': 100, 'max_depth': 5, 'learning_rate': 0.05},
            {'n_estimators': 150, 'max_depth': 4, 'learning_rate': 0.08},
        ]

        for params in param_grid:
            try:
                model = lgb.LGBMRegressor(
                    **params,
                    random_state=42,
                    verbosity=-1
                )

                # Cross-validation score
                cv_scores = cross_val_score(
                    model, X_train_selected, y_train, cv=3,
                    scoring='r2'
                )
                score = np.mean(cv_scores)

                if score > best_score:
                    best_score = score
                    best_model = model
                    best_params = params

            except Exception as e:
                print(f"Failed to fit with params {params}: {e}")

        if best_model is None:
            raise ValueError("All ensemble models failed to fit")

        # Train best model
        if hasattr(best_model, 'fit') and 'sample_weight' in best_model.fit.__code__.co_varnames:
            best_model.fit(X_train_selected, y_train, sample_weight=exp_train)
        else:
            best_model.fit(X_train_selected, y_train)

        # Evaluate
        y_pred = best_model.predict(X_test_selected)
        r2 = r2_score(y_test, y_pred, sample_weight=exp_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred, sample_weight=exp_test))

        self.model = best_model
        self.model_type = "ensemble_lightgbm"

        return {
            'model_type': self.model_type,
            'r2_score': r2,
            'rmse': rmse,
            'best_params': best_params,
            'n_trials': len(param_grid),
            'n_features_selected': max_features
        }

    def fit(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Main fitting method that selects appropriate model tier"""
        self.sample_size = len(df)
        tier = self.get_model_tier(self.sample_size)

        print(f"Sample size: {self.sample_size}, Model tier: {tier}")

        # Prepare features (no interactions for small datasets to avoid complexity)
        X, y, exposure = self.prepare_features(df, create_interactions=False)

        # Fit appropriate model
        if tier == "regularized_linear":
            results = self.fit_regularized_linear(X, y, exposure)
        elif tier == "single_tree":
            results = self.fit_single_tree(X, y, exposure)
        elif tier == "ensemble":
            results = self.fit_ensemble(X, y, exposure)
        else:  # full_ml
            results = self.fit_ensemble(X, y, exposure)  # For now, same as ensemble

        self.fitted = True

        results.update({
            'sample_size': self.sample_size,
            'tier': tier,
            'n_features_raw': X.shape[1]
        })

        return results

    def predict(self, X_new: pd.DataFrame, exposure_new: np.ndarray = None) -> np.ndarray:
        """Make predictions with fitted model"""
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")

        # Prepare features (same as training but without interactions to avoid complexity)
        X_pred, _, _ = self.prepare_features(X_new, create_interactions=False)

        # Ensure same features as training
        missing_cols = set(self.feature_names) - set(X_pred.columns)
        extra_cols = set(X_pred.columns) - set(self.feature_names)

        # Add missing columns with zeros
        for col in missing_cols:
            X_pred[col] = 0

        # Remove extra columns and reorder to match training
        X_pred = X_pred[self.feature_names]

        # Apply same preprocessing - convert to numpy to avoid feature name issues
        if self.scaler is not None:
            X_pred_scaled = self.scaler.transform(X_pred.values)  # Use .values to avoid feature name checks
            if self.feature_selector is not None:
                X_pred_selected = self.feature_selector.transform(X_pred_scaled)
                predictions = self.model.predict(X_pred_selected)
            else:
                predictions = self.model.predict(X_pred_scaled)
        else:
            predictions = self.model.predict(X_pred.values)

        # Convert back to counts if exposure provided
        if exposure_new is not None:
            predictions = predictions * exposure_new

        return np.maximum(0, predictions)  # Ensure non-negative

    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """Get feature importance if available"""
        if not self.fitted:
            return None

        importance = None

        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            importance = np.abs(self.model.coef_).flatten()

        if importance is not None and self.feature_selector is not None:
            selected_features = self.feature_selector.get_feature_names_out(self.feature_names)
            return pd.DataFrame({
                'feature': selected_features,
                'importance': importance
            }).sort_values('importance', ascending=False)

        return None

    def save_model(self, filepath: str):
        """Save fitted model"""
        if not self.fitted:
            raise ValueError("Cannot save unfitted model")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_selector': self.feature_selector,
            'feature_names': self.feature_names,
            'model_type': self.model_type,
            'sample_size': self.sample_size,
            'fitted': self.fitted
        }

        joblib.dump(model_data, filepath)

    def load_model(self, filepath: str):
        """Load fitted model"""
        model_data = joblib.load(filepath)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_selector = model_data['feature_selector']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        self.sample_size = model_data['sample_size']
        self.fitted = model_data['fitted']