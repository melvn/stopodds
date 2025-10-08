"""
Test the trained LightGBM model with SHAP explanations
"""

import pandas as pd
from train import StopOddsModeler
import glob
import os

def test_model():
    """Test model loading and prediction"""
    # Find the latest model
    model_files = glob.glob("/tmp/stopodds_model_*.lgb")
    if not model_files:
        print("No model files found")
        return
    
    latest_model = max(model_files, key=os.path.getctime)
    print(f"Loading model: {latest_model}")
    
    # Load model
    modeler = StopOddsModeler()
    modeler.load_model(latest_model)
    
    print(f"Model type: {modeler.model_type}")
    print(f"Feature names: {modeler.feature_names}")
    print(f"SHAP explainer: {modeler.shap_explainer is not None}")
    
    # Create test data
    test_data = {
        'age_bracket': ['18-24'],
        'gender': ['Male'],
        'ethnicity': ['South Asian'],
        'skin_tone': [None],
        'height_bracket': [None],
        'visible_disability': [False],
        'concession': [False]
    }
    
    df = pd.DataFrame(test_data)
    print(f"Input data: {df.iloc[0].to_dict()}")
    
    # Prepare features
    df_processed = modeler.prepare_features(df, for_lgb=True)
    print(f"Processed features: {list(df_processed.columns)}")
    
    # Get feature columns
    feature_cols = [col for col in df_processed.columns 
                   if col not in ['stops', 'trips', 'id', 'created_at', 'user_agent_hash']]
    X = df_processed[feature_cols]
    
    # Make prediction
    pred_result = modeler.predict_with_uncertainty(X)
    rate = pred_result['prediction'][0] * 100
    ci_lower = pred_result['lower_ci'][0] * 100
    ci_upper = pred_result['upper_ci'][0] * 100
    
    print(f"Prediction: {rate:.1f}% (CI: {ci_lower:.1f}% - {ci_upper:.1f}%)")
    
    # Test explanations
    explanations = modeler.explain_prediction(X, max_features=3)
    print(f"Explanation: {explanations[0]}")

if __name__ == "__main__":
    test_model()