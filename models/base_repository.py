"""
Base Repository - Provides common database operations

This is the parent class for all repositories, providing a consistent
interface for database operations and reducing code duplication.
"""
from config.database import get_db_connection
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseRepository:
    """
    Base class for all repositories with common DB operations.
    
    Usage:
        class EmployeeRepository(BaseRepository):
            def get_by_id(self, id):
                return self.execute_query("SELECT * FROM employees WHERE id = %s", (id,), fetch_one=True)
    """
    
    def __init__(self):
        self.get_connection = get_db_connection
    
    def execute_query(self, query, params=None, fetch_one=False):
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string with %s placeholders
            params: Tuple of parameters
            fetch_one: If True, return single row, else all rows
            
        Returns:
            dict or list: Query results
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            
            logger.debug(f"Query executed: {query[:100]}... | Rows: {1 if fetch_one else len(result) if result else 0}")
            return result
            
        except Exception as e:
            logger.error(f"Query failed: {query[:100]}... | Error: {e}")
            raise
        finally:
            conn.close()
    
    def execute_write(self, query, params=None):
        """
        Execute INSERT/UPDATE/DELETE and return affected rows or last insert ID.
        
        Args:
            query: SQL query string
            params: Tuple of parameters
            
        Returns:
            int: Last inserted ID (for INSERT) or row count (for UPDATE/DELETE)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            
            result = cursor.lastrowid or cursor.rowcount
            logger.debug(f"Write executed: {query[:100]}... | Result: {result}")
            return result
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Write failed: {query[:100]}... | Error: {e}")
            raise
        finally:
            conn.close()
    
    def execute_many(self, query, params_list):
        """
        Execute batch operations.
        
        Args:
            query: SQL query string
            params_list: List of tuples with parameters
            
        Returns:
            int: Number of affected rows
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            
            result = cursor.rowcount
            logger.debug(f"Batch executed: {query[:100]}... | Rows: {result}")
            return result
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Batch failed: {query[:100]}... | Error: {e}")
            raise
        finally:
            conn.close()
    
    def execute_transaction(self, queries_with_params):
        """
        Execute multiple queries in a single transaction.
        
        Args:
            queries_with_params: List of (query, params) tuples
            
        Returns:
            bool: True if all queries succeeded
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            for query, params in queries_with_params:
                cursor.execute(query, params or ())
            
            conn.commit()
            logger.debug(f"Transaction completed: {len(queries_with_params)} queries")
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction failed: {e}")
            raise
        finally:
            conn.close()
    
    def get_count(self, table, where_clause=None, params=None):
        """
        Get count of records in a table.
        
        Args:
            table: Table name
            where_clause: Optional WHERE clause (without 'WHERE' keyword)
            params: Parameters for WHERE clause
            
        Returns:
            int: Count of records
        """
        query = f"SELECT COUNT(*) as count FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        result = self.execute_query(query, params, fetch_one=True)
        return result['count'] if result else 0
