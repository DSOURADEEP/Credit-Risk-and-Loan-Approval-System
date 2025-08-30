from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from mysql.connector import Error
import logging
from app.database import execute_query, execute_many

logger = logging.getLogger(__name__)

class BaseRepository(ABC):
    """Base repository class with common database operations"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """Create a new record and return its ID"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            
            result = execute_query(query, tuple(data.values()))
            logger.info(f"Created record in {self.table_name} with ID: {result}")
            return result
            
        except Error as e:
            logger.error(f"Error creating record in {self.table_name}: {e}")
            raise
    
    def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Get a record by its ID"""
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id = %s"
            result = execute_query(query, (record_id,), fetch_one=True)
            
            if result:
                logger.info(f"Retrieved record from {self.table_name} with ID: {record_id}")
            
            return result
            
        except Error as e:
            logger.error(f"Error retrieving record from {self.table_name}: {e}")
            raise
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all records with optional pagination"""
        try:
            query = f"SELECT * FROM {self.table_name}"
            params = []
            
            if limit:
                query += " LIMIT %s OFFSET %s"
                params = [limit, offset]
            
            result = execute_query(query, tuple(params), fetch_all=True)
            logger.info(f"Retrieved {len(result)} records from {self.table_name}")
            return result or []
            
        except Error as e:
            logger.error(f"Error retrieving records from {self.table_name}: {e}")
            raise
    
    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        """Update a record by its ID"""
        try:
            if not data:
                return False
            
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s"
            params = list(data.values()) + [record_id]
            
            rows_affected = execute_query(query, tuple(params))
            success = rows_affected > 0
            
            if success:
                logger.info(f"Updated record in {self.table_name} with ID: {record_id}")
            
            return success
            
        except Error as e:
            logger.error(f"Error updating record in {self.table_name}: {e}")
            raise
    
    def delete(self, record_id: int) -> bool:
        """Delete a record by its ID"""
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            rows_affected = execute_query(query, (record_id,))
            success = rows_affected > 0
            
            if success:
                logger.info(f"Deleted record from {self.table_name} with ID: {record_id}")
            
            return success
            
        except Error as e:
            logger.error(f"Error deleting record from {self.table_name}: {e}")
            raise
    
    def exists(self, record_id: int) -> bool:
        """Check if a record exists by its ID"""
        try:
            query = f"SELECT 1 FROM {self.table_name} WHERE id = %s LIMIT 1"
            result = execute_query(query, (record_id,), fetch_one=True)
            return result is not None
            
        except Error as e:
            logger.error(f"Error checking existence in {self.table_name}: {e}")
            raise
    
    def count(self, conditions: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional conditions"""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            params = []
            
            if conditions:
                where_clause = ' AND '.join([f"{key} = %s" for key in conditions.keys()])
                query += f" WHERE {where_clause}"
                params = list(conditions.values())
            
            result = execute_query(query, tuple(params), fetch_one=True)
            return result['count'] if result else 0
            
        except Error as e:
            logger.error(f"Error counting records in {self.table_name}: {e}")
            raise