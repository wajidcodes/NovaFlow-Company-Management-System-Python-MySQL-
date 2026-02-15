"""
Employee Service

Business logic for employee CRUD operations.
Encapsulates complex operations like creating employees with subtypes.
"""
from models.employee_repository import EmployeeRepository
from models.base_repository import BaseRepository
from services.auth_service import AuthService
from utils.logger import setup_logger
from config.database import get_db_connection

logger = setup_logger(__name__)


class EmployeeService:
    """
    Service layer for employee operations.
    Handles business logic that spans multiple tables.
    """
    
    def __init__(self):
        self.repo = EmployeeRepository()
    
    def create_employee(self, data: dict) -> tuple:
        """
        Create a new employee with all related records.
        
        Args:
            data: Dictionary containing:
                - name, email, phone, national_insurance
                - date_of_birth, address, start_date
                - department_id, person_type
                - fixed_salary (for HOD/Supervisor)
                - hourly_rate (for Salesman/General Employee)
                - commission_rate (for Salesman)
                - supervisor_id (optional)
                
        Returns:
            tuple: (person_id, error_message)
                   On success: (id, None)
                   On failure: (None, error_string)
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Generate default password hash
            password_hash = AuthService.hash_password('password123')
            
            # Insert into person table
            cursor.execute("""
                INSERT INTO person (
                    name, email, phone, national_insurance, date_of_birth,
                    address, start_date, department_id, person_type,
                    password_hash, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['name'], data['email'], data['phone'],
                data['national_insurance'], data.get('date_of_birth'),
                data.get('address'), data.get('start_date'),
                data['department_id'], data['person_type'],
                password_hash, data.get('is_active', True)
            ))
            
            person_id = cursor.lastrowid
            person_type = data['person_type']
            
            # Insert into specialization table
            if person_type in ['HOD', 'SUPERVISOR']:
                table = 'hod' if person_type == 'HOD' else 'supervisor'
                cursor.execute(
                    f"INSERT INTO {table} (person_id, fixed_salary) VALUES (%s, %s)",
                    (person_id, data['fixed_salary'])
                )
            elif person_type == 'SALESMAN':
                cursor.execute(
                    "INSERT INTO salesman (person_id, hourly_rate, commission_rate) VALUES (%s, %s, %s)",
                    (person_id, data['hourly_rate'], data['commission_rate'])
                )
            elif person_type == 'GENERAL_EMPLOYEE':
                cursor.execute(
                    "INSERT INTO general_employee (person_id, hourly_rate) VALUES (%s, %s)",
                    (person_id, data['hourly_rate'])
                )
            
            # Assign supervisor if applicable
            if person_type not in ['HOD', 'SUPERVISOR'] and data.get('supervisor_id'):
                cursor.execute(
                    "INSERT INTO emp_supervisor (employee_id, supervisor_id) VALUES (%s, %s)",
                    (person_id, data['supervisor_id'])
                )
            
            conn.commit()
            logger.info(f"Employee created: {data['name']} (ID: {person_id})")
            return person_id, None
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create employee: {e}")
            return None, str(e)
        finally:
            conn.close()
    
    def update_employee(self, person_id: int, data: dict) -> tuple:
        """
        Update an existing employee.
        
        Args:
            person_id: Employee ID to update
            data: Dictionary with fields to update
            
        Returns:
            tuple: (success, error_message)
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Update person table
            cursor.execute("""
                UPDATE person SET
                    name=%s, email=%s, phone=%s, national_insurance=%s,
                    date_of_birth=%s, address=%s, start_date=%s,
                    department_id=%s, is_active=%s
                WHERE person_id=%s
            """, (
                data['name'], data['email'], data['phone'],
                data['national_insurance'], data.get('date_of_birth'),
                data.get('address'), data.get('start_date'),
                data['department_id'], data.get('is_active', True),
                person_id
            ))
            
            # Update specialization table
            person_type = data['person_type']
            
            if person_type in ['HOD', 'SUPERVISOR']:
                table = 'hod' if person_type == 'HOD' else 'supervisor'
                cursor.execute(
                    f"UPDATE {table} SET fixed_salary=%s WHERE person_id=%s",
                    (data['fixed_salary'], person_id)
                )
            elif person_type == 'SALESMAN':
                cursor.execute(
                    "UPDATE salesman SET hourly_rate=%s, commission_rate=%s WHERE person_id=%s",
                    (data['hourly_rate'], data['commission_rate'], person_id)
                )
            elif person_type == 'GENERAL_EMPLOYEE':
                cursor.execute(
                    "UPDATE general_employee SET hourly_rate=%s WHERE person_id=%s",
                    (data['hourly_rate'], person_id)
                )
            
            conn.commit()
            logger.info(f"Employee updated: ID {person_id}")
            return True, None
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update employee {person_id}: {e}")
            return False, str(e)
        finally:
            conn.close()
    
    def deactivate_employee(self, person_id: int) -> tuple:
        """
        Soft delete an employee (set is_active = False).
        
        Args:
            person_id: Employee ID to deactivate
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            self.repo.deactivate(person_id)
            logger.info(f"Employee deactivated: ID {person_id}")
            return True, None
        except Exception as e:
            logger.error(f"Failed to deactivate employee {person_id}: {e}")
            return False, str(e)
    
    def activate_employee(self, person_id: int) -> tuple:
        """
        Reactivate a deactivated employee.
        
        Args:
            person_id: Employee ID to activate
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            self.repo.activate(person_id)
            logger.info(f"Employee activated: ID {person_id}")
            return True, None
        except Exception as e:
            logger.error(f"Failed to activate employee {person_id}: {e}")
            return False, str(e)
    
    def get_departments(self) -> list:
        """Get all departments for dropdown."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            return cursor.fetchall()
        finally:
            conn.close()
    
    def get_supervisors(self) -> list:
        """Get all active supervisors for dropdown."""
        return self.repo.get_supervisors()
