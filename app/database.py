import mysql.connector
from mysql.connector import pooling, Error
from contextlib import contextmanager
import logging
from typing import Optional, Dict, Any
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection manager with connection pooling"""
    
    def __init__(self):
        self.pool: Optional[pooling.MySQLConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize MySQL connection pool"""
        try:
            pool_config = {
                'pool_name': 'loan_approval_pool',
                'pool_size': 10,
                'pool_reset_session': True,
                'host': settings.DATABASE_HOST,
                'port': settings.DATABASE_PORT,
                'database': settings.DATABASE_NAME,
                'user': settings.DATABASE_USER,
                'password': settings.DATABASE_PASSWORD,
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'autocommit': False,
                'raise_on_warnings': True
            }
            
            self.pool = pooling.MySQLConnectionPool(**pool_config)
            logger.info("Database connection pool initialized successfully")
            
        except Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = self.pool.get_connection()
            yield connection
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """Context manager for database cursors"""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary)
            try:
                yield cursor, connection
            except Error as e:
                connection.rollback()
                logger.error(f"Database cursor error: {e}")
                raise
            else:
                connection.commit()
            finally:
                cursor.close()

# Global database manager instance
db_manager = DatabaseManager()

def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False) -> Optional[Any]:
    """Execute a database query with optional parameters"""
    try:
        with db_manager.get_cursor() as (cursor, connection):
            cursor.execute(query, params or ())
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
                
    except Error as e:
        logger.error(f"Query execution error: {e}")
        raise

def execute_many(query: str, params_list: list) -> int:
    """Execute a query with multiple parameter sets"""
    try:
        with db_manager.get_cursor() as (cursor, connection):
            cursor.executemany(query, params_list)
            return cursor.rowcount
            
    except Error as e:
        logger.error(f"Batch query execution error: {e}")
        raise

def test_connection() -> bool:
    """Test database connectivity"""
    try:
        with db_manager.get_connection() as connection:
            if connection.is_connected():
                logger.info("Database connection test successful")
                return True
    except Error as e:
        logger.error(f"Database connection test failed: {e}")
        return False