#!/usr/bin/env python3
"""
Train machine learning models for loan approval prediction
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import logging
from typing import Dict, Tuple, Any
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoanApprovalModelTrainer:
    """Train and evaluate loan approval prediction models"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoder = LabelEncoder()
        self.feature_columns = [
            'age', 'salary', 'credit_score', 'loan_amount', 
            'existing_loans', 'employment_years', 'repayment_history'
        ]
        self.target_column = 'approval_decision'
    
    def load_and_prepare_data(self, data_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load and prepare training data"""
        logger.info(f"Loading data from {data_path}")
        
        # Load data
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} samples")
        
        # Check for missing values
        if df.isnull().sum().sum() > 0:
            logger.warning("Found missing values, filling with median/mode")
            for col in self.feature_columns:
                if df[col].dtype in ['int64', 'float64']:
                    df[col].fillna(df[col].median(), inplace=True)
                else:
                    df[col].fillna(df[col].mode()[0], inplace=True)
        
        # Prepare features
        X = df[self.feature_columns].copy()
        
        # Add derived features
        X['monthly_income'] = df['monthly_income'] if 'monthly_income' in df.columns else X['salary'] / 12
        X['loan_to_income_ratio'] = X['loan_amount'] / X['salary']
        X['debt_burden'] = X['existing_loans'] * 500  # Estimated monthly debt
        X['debt_to_income_ratio'] = X['debt_burden'] / X['monthly_income']
        
        # Update feature columns
        self.feature_columns = X.columns.tolist()
        
        # Prepare target
        y = self.label_encoder.fit_transform(df[self.target_column])
        
        logger.info(f"Features: {self.feature_columns}")
        logger.info(f"Target classes: {self.label_encoder.classes_}")
        logger.info(f"Class distribution: {np.bincount(y)}")
        
        return X.values, y
    
    def train_random_forest(self, X_train: np.ndarray, y_train: np.ndarray) -> RandomForestClassifier:
        """Train Random Forest model with hyperparameter tuning"""
        logger.info("Training Random Forest model...")
        
        # Define parameter grid for tuning
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2']
        }
        
        # Create base model
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        
        # Perform grid search
        logger.info("Performing hyperparameter tuning...")
        grid_search = GridSearchCV(
            rf, param_grid, cv=5, scoring='f1_weighted', 
            n_jobs=-1, verbose=1
        )
        grid_search.fit(X_train, y_train)
        
        best_rf = grid_search.best_estimator_
        logger.info(f"Best RF parameters: {grid_search.best_params_}")
        logger.info(f"Best RF CV score: {grid_search.best_score_:.4f}")
        
        return best_rf
    
    def train_logistic_regression(self, X_train: np.ndarray, y_train: np.ndarray) -> Tuple[LogisticRegression, StandardScaler]:
        """Train Logistic Regression model with feature scaling"""
        logger.info("Training Logistic Regression model...")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        # Define parameter grid
        param_grid = {
            'C': [0.01, 0.1, 1, 10, 100],
            'penalty': ['l1', 'l2'],
            'solver': ['liblinear', 'saga'],
            'max_iter': [1000, 2000]
        }
        
        # Create base model
        lr = LogisticRegression(random_state=42, multi_class='ovr')
        
        # Perform grid search
        logger.info("Performing hyperparameter tuning...")
        grid_search = GridSearchCV(
            lr, param_grid, cv=5, scoring='f1_weighted', 
            n_jobs=-1, verbose=1
        )
        grid_search.fit(X_train_scaled, y_train)
        
        best_lr = grid_search.best_estimator_
        logger.info(f"Best LR parameters: {grid_search.best_params_}")
        logger.info(f"Best LR CV score: {grid_search.best_score_:.4f}")
        
        return best_lr, scaler
    
    def evaluate_model(self, model, X_test: np.ndarray, y_test: np.ndarray, 
                      model_name: str, scaler=None) -> Dict[str, Any]:
        """Evaluate model performance"""
        logger.info(f"Evaluating {model_name} model...")
        
        # Prepare test data
        X_test_processed = scaler.transform(X_test) if scaler else X_test
        
        # Make predictions
        y_pred = model.predict(X_test_processed)
        y_pred_proba = model.predict_proba(X_test_processed)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # ROC AUC for multiclass
        try:
            auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
        except ValueError:
            auc = 0.0
        
        # Cross-validation score
        cv_scores = cross_val_score(model, X_test_processed, y_test, cv=5, scoring='f1_weighted')
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': auc,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'classification_report': classification_report(y_test, y_pred, 
                                                         target_names=self.label_encoder.classes_,
                                                         output_dict=True)
        }
        
        logger.info(f"{model_name} Metrics:")
        logger.info(f"  Accuracy: {accuracy:.4f}")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall: {recall:.4f}")
        logger.info(f"  F1-Score: {f1:.4f}")
        logger.info(f"  ROC-AUC: {auc:.4f}")
        logger.info(f"  CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        return metrics
    
    def get_feature_importance(self, model, model_name: str) -> Dict[str, float]:
        """Get feature importance from trained model"""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # For logistic regression, use absolute values of coefficients
            importance = np.abs(model.coef_).mean(axis=0)
        else:
            return {}
        
        feature_importance = dict(zip(self.feature_columns, importance))
        
        # Sort by importance
        sorted_importance = dict(sorted(feature_importance.items(), 
                                      key=lambda x: x[1], reverse=True))
        
        logger.info(f"{model_name} Feature Importance:")
        for feature, imp in sorted_importance.items():
            logger.info(f"  {feature}: {imp:.4f}")
        
        return sorted_importance
    
    def save_models(self, models_dir: Path):
        """Save trained models and metadata"""
        models_dir.mkdir(exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            model_path = models_dir / f"{name}_model.joblib"
            joblib.dump(model, model_path)
            logger.info(f"Saved {name} model to {model_path}")
        
        # Save scalers
        for name, scaler in self.scalers.items():
            scaler_path = models_dir / f"{name}_scaler.joblib"
            joblib.dump(scaler, scaler_path)
            logger.info(f"Saved {name} scaler to {scaler_path}")
        
        # Save label encoder
        encoder_path = models_dir / "label_encoder.joblib"
        joblib.dump(self.label_encoder, encoder_path)
        logger.info(f"Saved label encoder to {encoder_path}")
        
        # Save feature columns
        features_path = models_dir / "feature_columns.json"
        with open(features_path, 'w') as f:
            json.dump(self.feature_columns, f)
        logger.info(f"Saved feature columns to {features_path}")
    
    def train_all_models(self, data_path: str, models_dir: Path):
        """Train all models and save results"""
        # Load and prepare data
        X, y = self.load_and_prepare_data(data_path)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"Training set size: {len(X_train)}")
        logger.info(f"Test set size: {len(X_test)}")
        
        # Train Random Forest
        rf_model = self.train_random_forest(X_train, y_train)
        self.models['random_forest'] = rf_model
        
        # Train Logistic Regression
        lr_model, lr_scaler = self.train_logistic_regression(X_train, y_train)
        self.models['logistic_regression'] = lr_model
        self.scalers['logistic_regression'] = lr_scaler
        
        # Evaluate models
        results = {}
        
        # Evaluate Random Forest
        rf_metrics = self.evaluate_model(rf_model, X_test, y_test, "Random Forest")
        rf_importance = self.get_feature_importance(rf_model, "Random Forest")
        results['random_forest'] = {
            'metrics': rf_metrics,
            'feature_importance': rf_importance
        }
        
        # Evaluate Logistic Regression
        lr_metrics = self.evaluate_model(lr_model, X_test, y_test, "Logistic Regression", lr_scaler)
        lr_importance = self.get_feature_importance(lr_model, "Logistic Regression")
        results['logistic_regression'] = {
            'metrics': lr_metrics,
            'feature_importance': lr_importance
        }
        
        # Save models
        self.save_models(models_dir)
        
        # Save results
        results_path = models_dir / "training_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Saved training results to {results_path}")
        
        return results

def main():
    """Main training function"""
    
    # Set up paths
    data_dir = Path("data")
    models_dir = Path("models")
    
    # Create directories
    models_dir.mkdir(exist_ok=True)
    
    # Check if training data exists
    training_file = data_dir / "training_data_large.csv"
    if not training_file.exists():
        logger.error(f"Training data not found at {training_file}")
        logger.info("Please run generate_training_data.py first")
        return
    
    # Train models
    trainer = LoanApprovalModelTrainer()
    results = trainer.train_all_models(str(training_file), models_dir)
    
    # Print summary
    print("\n" + "="*50)
    print("TRAINING SUMMARY")
    print("="*50)
    
    for model_name, result in results.items():
        metrics = result['metrics']
        print(f"\n{model_name.upper()}:")
        print(f"  Accuracy: {metrics['accuracy']:.4f}")
        print(f"  F1-Score: {metrics['f1_score']:.4f}")
        print(f"  ROC-AUC: {metrics['roc_auc']:.4f}")
        
        print(f"  Top 3 Features:")
        for i, (feature, importance) in enumerate(list(result['feature_importance'].items())[:3]):
            print(f"    {i+1}. {feature}: {importance:.4f}")

if __name__ == "__main__":
    main()