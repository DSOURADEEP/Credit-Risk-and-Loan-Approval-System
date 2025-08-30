import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import json
from dataclasses import dataclass
from app.models.ml_prediction import MLPredictionRequest, MLPredictionResponse, CombinedMLPrediction

logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    """Information about a loaded ML model"""
    model: Any
    scaler: Optional[Any] = None
    feature_columns: List[str] = None
    model_type: str = ""

class MLModelService:
    """Service for loading and using ML models for loan approval prediction"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models: Dict[str, ModelInfo] = {}
        self.label_encoder = None
        self.feature_columns = []
        self._load_models()
    
    def _load_models(self):
        """Load all trained models and associated components"""
        try:
            logger.info(f"Loading ML models from {self.models_dir}")
            
            # Load feature columns
            features_path = self.models_dir / "feature_columns.json"
            if features_path.exists():
                with open(features_path, 'r') as f:
                    self.feature_columns = json.load(f)
                logger.info(f"Loaded feature columns: {self.feature_columns}")
            else:
                logger.warning("Feature columns file not found")
                return
            
            # Load label encoder
            encoder_path = self.models_dir / "label_encoder.joblib"
            if encoder_path.exists():
                self.label_encoder = joblib.load(encoder_path)
                logger.info(f"Loaded label encoder with classes: {self.label_encoder.classes_}")
            else:
                logger.warning("Label encoder not found")
                return
            
            # Load Random Forest model
            rf_model_path = self.models_dir / "random_forest_model.joblib"
            if rf_model_path.exists():
                rf_model = joblib.load(rf_model_path)
                self.models['random_forest'] = ModelInfo(
                    model=rf_model,
                    feature_columns=self.feature_columns,
                    model_type="RandomForest"
                )
                logger.info("Loaded Random Forest model")
            else:
                logger.warning("Random Forest model not found")
            
            # Load Logistic Regression model and scaler
            lr_model_path = self.models_dir / "logistic_regression_model.joblib"
            lr_scaler_path = self.models_dir / "logistic_regression_scaler.joblib"
            
            if lr_model_path.exists() and lr_scaler_path.exists():
                lr_model = joblib.load(lr_model_path)
                lr_scaler = joblib.load(lr_scaler_path)
                self.models['logistic_regression'] = ModelInfo(
                    model=lr_model,
                    scaler=lr_scaler,
                    feature_columns=self.feature_columns,
                    model_type="LogisticRegression"
                )
                logger.info("Loaded Logistic Regression model and scaler")
            else:
                logger.warning("Logistic Regression model or scaler not found")
            
            if not self.models:
                logger.error("No models loaded successfully")
            else:
                logger.info(f"Successfully loaded {len(self.models)} models")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def _prepare_features(self, request: MLPredictionRequest) -> np.ndarray:
        """Prepare feature vector from prediction request"""
        try:
            # Create base features
            features = {
                'age': request.age,
                'salary': request.salary,
                'credit_score': request.credit_score,
                'loan_amount': request.loan_amount,
                'existing_loans': request.existing_loans,
                'employment_years': request.employment_years,
                'repayment_history': getattr(request, 'repayment_history', 
                                           self._estimate_repayment_history(request.credit_score))
            }
            
            # Add derived features
            features['monthly_income'] = request.monthly_income
            features['loan_to_income_ratio'] = request.loan_amount / request.salary
            features['debt_burden'] = request.existing_loans * 500  # Estimated monthly debt
            features['debt_to_income_ratio'] = features['debt_burden'] / request.monthly_income
            
            # Create feature vector in the correct order
            feature_vector = []
            for col in self.feature_columns:
                if col in features:
                    feature_vector.append(features[col])
                else:
                    logger.warning(f"Feature {col} not found, using 0")
                    feature_vector.append(0)
            
            return np.array(feature_vector).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            raise
    
    def _estimate_repayment_history(self, credit_score: int) -> int:
        """Estimate repayment history score based on credit score"""
        # Simple mapping from credit score to repayment history
        return max(0, min(100, int((credit_score - 300) / (850 - 300) * 100)))
    
    def predict_single_model(self, model_name: str, request: MLPredictionRequest) -> MLPredictionResponse:
        """Make prediction using a single model"""
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model_info = self.models[model_name]
            
            # Prepare features
            X = self._prepare_features(request)
            
            # Apply scaling if needed
            if model_info.scaler:
                X = model_info.scaler.transform(X)
            
            # Make prediction
            prediction_encoded = model_info.model.predict(X)[0]
            prediction_proba = model_info.model.predict_proba(X)[0]
            
            # Decode prediction
            prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
            
            # Get probability for the predicted class
            probability_score = prediction_proba[prediction_encoded]
            
            # Create feature vector for response
            feature_dict = dict(zip(self.feature_columns, X.flatten().tolist()))
            
            return MLPredictionResponse(
                model_name=model_info.model_type,
                prediction=prediction,
                probability_score=probability_score,
                confidence="high" if probability_score >= 0.8 else "medium" if probability_score >= 0.6 else "low",
                feature_vector=feature_dict
            )
            
        except Exception as e:
            logger.error(f"Error making prediction with {model_name}: {e}")
            raise
    
    def predict_combined(self, request: MLPredictionRequest) -> CombinedMLPrediction:
        """Make predictions using both models and combine results"""
        try:
            # Get predictions from both models
            rf_prediction = self.predict_single_model('random_forest', request)
            lr_prediction = self.predict_single_model('logistic_regression', request)
            
            # Check consensus
            consensus = rf_prediction.prediction == lr_prediction.prediction
            
            # Calculate average probability
            avg_probability = (rf_prediction.probability_score + lr_prediction.probability_score) / 2
            
            # Determine final decision
            if consensus:
                # Models agree
                final_decision = rf_prediction.prediction
            else:
                # Models disagree - use more conservative approach
                if avg_probability < 0.6:
                    final_decision = "manual_review"
                else:
                    # Use the prediction with higher confidence
                    if rf_prediction.probability_score > lr_prediction.probability_score:
                        final_decision = rf_prediction.prediction
                    else:
                        final_decision = lr_prediction.prediction
            
            return CombinedMLPrediction(
                random_forest=rf_prediction,
                logistic_regression=lr_prediction,
                final_decision=final_decision,
                consensus=consensus,
                average_probability=avg_probability
            )
            
        except Exception as e:
            logger.error(f"Error making combined prediction: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        info = {
            'models_loaded': list(self.models.keys()),
            'feature_columns': self.feature_columns,
            'target_classes': self.label_encoder.classes_.tolist() if self.label_encoder else [],
            'models_dir': str(self.models_dir)
        }
        
        for name, model_info in self.models.items():
            info[f'{name}_type'] = model_info.model_type
            info[f'{name}_has_scaler'] = model_info.scaler is not None
        
        return info
    
    def validate_request(self, request: MLPredictionRequest) -> bool:
        """Validate prediction request"""
        try:
            # Check required fields
            if request.salary <= 0:
                raise ValueError("Salary must be positive")
            
            if not (18 <= request.age <= 100):
                raise ValueError("Age must be between 18 and 100")
            
            if not (300 <= request.credit_score <= 850):
                raise ValueError("Credit score must be between 300 and 850")
            
            if request.loan_amount <= 0:
                raise ValueError("Loan amount must be positive")
            
            if request.existing_loans < 0:
                raise ValueError("Existing loans cannot be negative")
            
            if request.employment_years < 0:
                raise ValueError("Employment years cannot be negative")
            
            if request.monthly_income <= 0:
                raise ValueError("Monthly income must be positive")
            
            # Check consistency between salary and monthly income
            expected_monthly = request.salary / 12
            if abs(request.monthly_income - expected_monthly) > expected_monthly * 0.3:
                logger.warning("Monthly income seems inconsistent with annual salary")
            
            return True
            
        except ValueError as e:
            logger.error(f"Request validation failed: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if the service is ready to make predictions"""
        return (
            len(self.models) > 0 and 
            self.label_encoder is not None and 
            len(self.feature_columns) > 0
        )
    
    def reload_models(self):
        """Reload models from disk"""
        logger.info("Reloading ML models...")
        self.models.clear()
        self.label_encoder = None
        self.feature_columns = []
        self._load_models()

# Global ML service instance
ml_service = MLModelService()