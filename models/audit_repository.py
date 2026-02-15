"""
Audit Repository - Data access for audit logs
"""
from models.base_repository import BaseRepository

class AuditRepository(BaseRepository):
    """Repository for Audit Log operations"""
    
    def log_action(self, user_id, action_type, table_name, record_id, details=None):
        """
        Log a user action.
        
        Args:
            user_id: ID of user performing action
            action_type: CREATE, UPDATE, DELETE, LOGIN, etc.
            table_name: Affected table
            record_id: Affected record ID
            details: Optional description or JSON data
        """
        # Run asynchronously or quietly so it doesn't block/fail main flow
        try:
            query = """
                INSERT INTO audit_logs (user_id, action_type, table_name, record_id, details)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.execute_write(query, (user_id, action_type, table_name, record_id, details))
        except Exception as e:
            # Fallback to file logging if DB fails
            from utils.logger import setup_logger
            logger = setup_logger('audit_fallback')
            logger.error(f"Failed to write audit log: {e}")
            
    def get_logs(self, limit=100):
        """Get recent audit logs."""
        query = """
            SELECT a.*, p.name as user_name
            FROM audit_logs a
            LEFT JOIN person p ON a.user_id = p.person_id
            ORDER BY a.created_at DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
