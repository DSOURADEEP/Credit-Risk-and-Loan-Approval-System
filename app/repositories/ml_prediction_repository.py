from typing import Optional, List, Dict, Any
from mysql.connector import Error
import logging
import json
from app.repositories.base_repository import BaseRepository
from app.models.ml_prediction import MLPrediction
from app.database import execute_query

logger = logging.getLogger(__name__)

class MLPredictionRepository(BaseRepository):
    """Repository for ML prediction data operations"""
    
    def __init__(self):
        super().__init__("ml_predictions")
    
    def create_prediction(self, prediction_data: Dict[str, Any]) -> Optional[int]:
        """Create a new ML prediction record"""
        try:
            # Validate required fields
            required_fields = ['application_id', 'model_name', 'prediction', 'probability_score']
            for field in required_fields:
                if field not in prediction_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Convert feature_vector to JSON string if it's a dict
            if 'feature_vector' in prediction_data and isinstance(prediction_data['feature_vector'], dict):
                prediction_data['feature_vector'] = json.dumps(prediction_data['feature_vector'])
            
            prediction_id = self.create(prediction_data)
            logger.info(f"Created ML prediction with ID: {prediction_id}")
            return prediction_id
            
        except Error as e:
            logger.error(f"Error creating ML prediction: {e}")
            raise
    
    def get_prediction_by_id(self, prediction_id: int) -> Optional[MLPrediction]:
        """Get ML prediction by ID and return MLPrediction object"""
        try:
            result = self.get_by_id(prediction_id)
            if result:
                # Parse feature_vector JSON
                feature_vector = None
                if result['feature_vector']:
                    try:
                        feature_vector = json.loads(result['feature_vector'])
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in feature_vector for prediction {prediction_id}")
                
                return MLPrediction(
                    id=result['id'],
                    application_id=result['application_id'],
                    model_name=result['model_name'],
                    prediction=result['prediction'],
                    probability_score=float(result['probability_score']),
                    feature_vector=feature_vector,
                    created_at=result['created_at']
                )
            return None
            
        except Error as e:
            logger.error(f"Error retrieving ML prediction {prediction_id}: {e}")
            raise
    
    def get_predictions_by_application_id(self, application_id: int) -> List[MLPrediction]:
        """Get all ML predictions for a specific loan application"""
        try:
            query = """
                SELECT * FROM ml_predictions 
                WHERE application_id = %s 
                ORDER BY created_at DESC
            """
            results = execute_query(query, (application_id,), fetch_all=True)
            
            predictions = []
            for result in results:
                # Parse feature_vector JSON
                feature_vector = None
                if result['feature_vector']:
                    try:
                        feature_vector = json.loads(result['feature_vector'])
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in feature_vector for prediction {result['id']}")
                
                predictions.append(MLPrediction(
                    id=result['id'],
                    application_id=result['application_id'],
                    model_name=result['model_name'],
                    prediction=result['prediction'],
                    probability_score=float(result['probability_score']),
                    feature_vector=feature_vector,
                    created_at=result['created_at']
                ))
            
            return predictions
            
        except Error as e:
            logger.error(f"Error retrieving predictions for application {application_id}: {e}")
            raise
    
    def get_predictions_by_model(self, model_name: str) -> List[MLPrediction]:
        """Get all predictions for a specific model"""
        try:
            query = """
                SELECT * FROM ml_predictions 
                WHERE model_name = %s 
                ORDER BY created_at DESC
            """
            results = execute_query(query, (model_name,), fetch_all=True)
            
            predictions = []
            for result in results:
                # Parse feature_vector JSON
                feature_vector = None
                if result['feature_vector']:
                    try:
                        feature_vector = json.loads(result['feature_vector'])
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in feature_vector for prediction {result['id']}")
                
                predictions.append(MLPrediction(
                    id=result['id'],
                    application_id=result['application_id'],
                    model_name=result['model_name'],
                    prediction=result['prediction'],
                    probability_score=float(result['probability_score']),
                    feature_vector=feature_vector,
                    created_at=result['created_at']
                ))
            
            return predictions
            
        except Error as e:
            logger.error(f"Error retrieving predictions for model {model_name}: {e}")
            raise
    
    def get_model_performance_stats(self, model_name: str) -> Dict[str, Any]:
        """Get performance statistics for a specific model"""
        try:
            stats_query = """
                SELECT 
                    COUNT(*) as total_predictions,
                    SUM(CASE WHEN prediction = 'approved' THEN 1 ELSE 0 END) as approved_count,
                    SUM(CASE WHEN prediction = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
                    SUM(CASE WHEN prediction = 'manual_review' THEN 1 ELSE 0 END) as manual_review_count,
                    AVG(probability_score) as avg_probability,
                    MIN(probability_score) as min_probability,
                    MAX(probability_score) as max_probability
                FROM ml_predictions 
                WHERE model_name = %s
            """
            result = execute_query(stats_query, (model_name,), fetch_one=True)
            
            if result:
                total = result['total_predictions']
                return {
                    'model_name': model_name,
                    'total_predictions': total,
                    'approved_count': result['approved_count'],
                    'rejected_count': result['rejected_count'],
                    'manual_review_count': result['manual_review_count'],
                    'approval_rate': round((result['approved_count'] / total * 100), 2) if total > 0 else 0,
                    'average_probability': round(float(result['avg_probability']), 4) if result['avg_probability'] else 0,
                    'min_probability': float(result['min_probability']) if result['min_probability'] else 0,
                    'max_probability': float(result['max_probability']) if result['max_probability'] else 0
                }
            
            return {'model_name': model_name, 'total_predictions': 0}
            
        except Error as e:
            logger.error(f"Error retrieving model performance stats for {model_name}: {e}")
            raise
    
    def delete_predictions_by_application_id(self, application_id: int) -> bool:
        """Delete all predictions for a specific application"""
        try:
            query = "DELETE FROM ml_predictions WHERE application_id = %s"
            rows_affected = execute_query(query, (application_id,))
            success = rows_affected > 0
            
            if success:
                logger.info(f"Deleted {rows_affected} predictions for application {application_id}")
            
            return success
            
        except Error as e:
            logger.error(f"Error deleting predictions for application {application_id}: {e}")
            raise