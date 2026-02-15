"""
Authentication Service

Handles user authentication, password hashing, and session management.
Supports both legacy (unsalted) and new (salted) password hashes for
backward compatibility during migration.
"""
import hashlib
import secrets
import time
from config.database import get_db_connection
from utils.constants import PersonType, PERMISSIONS
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AuthService:
    """
    Handles authentication and authorization.
    
    Usage:
        auth = AuthService()
        user, error = auth.authenticate('email@example.com', 'password')
        if user:
            # Login successful
        else:
            # Show error message
    """
    
    # Session timeout in seconds (30 minutes)
    SESSION_TIMEOUT = 1800
    
    def __init__(self):
        self._session_start = None
        self._current_user = None
    
    @staticmethod
    def hash_password_legacy(password):
        """
        Legacy password hashing (SHA256 without salt).
        Used for backward compatibility with existing database.
        
        Args:
            password: Plain text password
            
        Returns:
            str: SHA256 hash
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def hash_password(password, salt=None):
        """
        Hash password with salt using SHA256.
        
        For new passwords, generates a random salt.
        For verification, uses the stored salt.
        
        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)
            
        Returns:
            str: Format "salt$hash"
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        salted = f"{salt}{password}"
        hashed = hashlib.sha256(salted.encode()).hexdigest()
        
        return f"{salt}${hashed}"
    
    @staticmethod
    def verify_password(password, stored_hash):
        """
        Verify password against stored hash.
        Supports both legacy (unsalted) and new (salted) formats.
        
        Args:
            password: Plain text password to verify
            stored_hash: Hash from database
            
        Returns:
            bool: True if password matches
        """
        # Check if it's a salted hash (contains $)
        if '$' in stored_hash:
            # New salted hash format
            salt, _ = stored_hash.split('$', 1)
            test_hash = AuthService.hash_password(password, salt)
            return test_hash == stored_hash
        else:
            # Legacy unsalted hash
            test_hash = AuthService.hash_password_legacy(password)
            return test_hash == stored_hash
    
    def authenticate(self, email, password):
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            tuple: (user_dict, error_message)
                   - On success: (user_dict, None)
                   - On failure: (None, error_string)
        """
        if not email or not password:
            return None, "Email and password are required"
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT person_id, name, email, person_type, 
                       department_id, is_active, password_hash
                FROM person 
                WHERE email = %s
            """, (email.strip().lower(),))
            
            user = cursor.fetchone()
            
            if not user:
                logger.warning(f"Login attempt with unknown email: {email}")
                return None, "Invalid email or password"
            
            if not user['is_active']:
                logger.warning(f"Login attempt on deactivated account: {email}")
                return None, "Account deactivated. Contact administrator."
            
            if not self.verify_password(password, user['password_hash']):
                logger.warning(f"Failed login attempt for: {email}")
                return None, "Invalid email or password"
            
            # Remove password hash from returned user dict
            del user['password_hash']
            
            # Start session
            self._session_start = time.time()
            self._current_user = user
            
            logger.info(f"User logged in: {user['name']} ({user['person_type']})")
            return user, None
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None, "Login failed. Please try again."
        finally:
            conn.close()
    
    def is_session_valid(self):
        """Check if current session is still valid."""
        if not self._session_start:
            return False
        
        elapsed = time.time() - self._session_start
        return elapsed < self.SESSION_TIMEOUT
    
    def refresh_session(self):
        """Refresh session timeout."""
        self._session_start = time.time()
    
    def logout(self):
        """Clear session."""
        if self._current_user:
            logger.info(f"User logged out: {self._current_user['name']}")
        self._session_start = None
        self._current_user = None
    
    @staticmethod
    def has_permission(user, permission):
        """
        Check if user has a specific permission.
        
        Args:
            user: User dict with 'person_type' key
            permission: Permission string to check
            
        Returns:
            bool: True if user has permission
        """
        try:
            user_type = PersonType(user['person_type'])
            return permission in PERMISSIONS.get(user_type, [])
        except (ValueError, KeyError):
            return False
    
    @staticmethod
    def get_user_permissions(user):
        """
        Get all permissions for a user.
        
        Args:
            user: User dict with 'person_type' key
            
        Returns:
            list: List of permission strings
        """
        try:
            user_type = PersonType(user['person_type'])
            return PERMISSIONS.get(user_type, [])
        except (ValueError, KeyError):
            return []
    
    @property
    def current_user(self):
        """Get current logged-in user."""
        return self._current_user


    def update_password(self, email, new_password):
        """
        Update user password.
        
        Args:
            email: User email
            new_password: New plain text password
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = get_db_connection()
        try:
            # Hash the new password
            hashed_password = self.hash_password(new_password)
            
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE person 
                SET password_hash = %s
                WHERE email = %s
            """, (hashed_password, email.strip().lower()))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Password updated for user: {email}")
                return True
            else:
                logger.warning(f"Password update failed - user not found: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Password update error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

# Singleton instance for easy access
_auth_service = None

def get_auth_service():
    """Get singleton AuthService instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
