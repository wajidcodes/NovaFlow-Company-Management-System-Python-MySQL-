"""
Database Configuration and Connection Management
"""
import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration from environment
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'company_management'),
    'charset': 'utf8mb4'
}


def get_db_connection():
    """
    Create and return a database connection.
    
    Returns:
        pymysql.Connection: Database connection with DictCursor
        
    Raises:
        pymysql.Error: If connection fails
    """
    return pymysql.connect(
        **DB_CONFIG,
        cursorclass=pymysql.cursors.DictCursor
    )


def test_connection():
    """
    Test database connectivity.
    
    Returns:
        tuple: (bool success, str message)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"


if __name__ == "__main__":
    # Test connection when run directly
    success, message = test_connection()
    print(message)
