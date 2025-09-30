import shap
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import io
import base64

class SHAPExplainer:
    def __init__(self, model, model_type: str, feature_names: List[str]):
        self.model = model
        self.model_type = model_type
        self.feature_names = feature_names
        self.explainer = None
        
        if model_type == 'lightgbm':
            self.explainer = shap.TreeExplainer(model)
        else:
            raise ValueError(f"SHAP explanations not supported for model type: {model_type}")
    
    def get_local_explanation(self, X: pd.DataFrame, max_features: int = 3) -> List[Dict[str, Any]]:
        """Get SHAP explanations for individual predictions"""
        if self.explainer is None:
            return []
        
        shap_values = self.explainer.shap_values(X)
        explanations = []
        
        for i in range(len(X)):
            # Get feature contributions
            feature_contributions = []
            for j, feature_name in enumerate(self.feature_names):
                contribution = shap_values[i][j]
                feature_contributions.append({
                    'feature': feature_name,
                    'value': float(X.iloc[i][j]),
                    'contribution': float(contribution),
                    'abs_contribution': float(abs(contribution))
                })
            
            # Sort by absolute contribution
            feature_contributions.sort(key=lambda x: x['abs_contribution'], reverse=True)
            
            # Generate human-readable explanation
            top_features = feature_contributions[:max_features]
            explanation_text = self._generate_explanation_text(top_features)
            
            explanations.append({
                'explanation_text': explanation_text,
                'top_features': top_features,
                'base_value': float(self.explainer.expected_value),
                'prediction_value': float(sum(contrib['contribution'] for contrib in feature_contributions) + self.explainer.expected_value)
            })
        
        return explanations
    
    def get_global_explanation(self, X: pd.DataFrame) -> Dict[str, Any]:
        """Get global SHAP summary"""
        if self.explainer is None:
            return {}
        
        shap_values = self.explainer.shap_values(X)
        
        # Calculate mean absolute SHAP values for feature importance
        mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
        
        feature_importance = []
        for i, feature_name in enumerate(self.feature_names):
            feature_importance.append({
                'feature': feature_name,
                'importance': float(mean_abs_shap[i])
            })
        
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'feature_importance': feature_importance,
            'base_value': float(self.explainer.expected_value)
        }
    
    def _generate_explanation_text(self, top_features: List[Dict[str, Any]]) -> str:
        """Generate human-readable explanation from SHAP values"""
        explanations = []
        
        for feature_data in top_features:
            feature = feature_data['feature']
            contribution = feature_data['contribution']
            value = feature_data['value']
            
            # Clean up feature names for display
            display_feature = self._clean_feature_name(feature)
            
            if contribution > 0:
                direction = "increases"
            else:
                direction = "decreases"
            
            # Format based on feature type
            if isinstance(value, bool) or feature.endswith(('_True', '_False')):
                if value > 0.5:  # Assuming dummy encoded
                    explanations.append(f"{display_feature} {direction} your risk")
                else:
                    explanations.append(f"Not having {display_feature} {direction} your risk")
            else:
                explanations.append(f"{display_feature} {direction} your risk")
        
        return "; ".join(explanations)
    
    def _clean_feature_name(self, feature: str) -> str:
        """Clean feature names for display"""
        # Remove dummy encoding suffixes
        feature = feature.replace('_Male', ' (Male)')
        feature = feature.replace('_Female', ' (Female)')
        feature = feature.replace('_Nonbinary', ' (Nonbinary)')
        feature = feature.replace('age_bracket_', 'Age ')
        feature = feature.replace('ethnicity_', '')
        feature = feature.replace('skin_tone_', 'Skin tone: ')
        feature = feature.replace('height_bracket_', 'Height ')
        feature = feature.replace('visible_disability', 'Visible disability')
        feature = feature.replace('concession', 'Concession/MIPE')
        
        return feature
    
    def generate_summary_plot(self, X: pd.DataFrame, max_display: int = 10) -> str:
        """Generate SHAP summary plot as base64 string"""
        if self.explainer is None:
            return ""
        
        try:
            shap_values = self.explainer.shap_values(X)
            
            plt.figure(figsize=(10, 6))
            shap.summary_plot(
                shap_values, 
                X, 
                feature_names=self.feature_names,
                max_display=max_display,
                show=False
            )
            
            # Convert plot to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return img_str
            
        except Exception as e:
            print(f"Error generating SHAP plot: {e}")
            return ""
    
    def generate_waterfall_plot(self, X: pd.DataFrame, index: int = 0) -> str:
        """Generate SHAP waterfall plot for a single prediction"""
        if self.explainer is None:
            return ""
        
        try:
            shap_values = self.explainer.shap_values(X.iloc[[index]])
            
            plt.figure(figsize=(10, 6))
            shap.waterfall_plot(
                shap.Explanation(
                    values=shap_values[0],
                    base_values=self.explainer.expected_value,
                    data=X.iloc[index].values,
                    feature_names=self.feature_names
                ),
                show=False
            )
            
            # Convert plot to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return img_str
            
        except Exception as e:
            print(f"Error generating waterfall plot: {e}")
            return ""