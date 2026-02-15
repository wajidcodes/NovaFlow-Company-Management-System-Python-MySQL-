"""
Employee Repository - Data access for employee operations
"""
from models.base_repository import BaseRepository
from utils.constants import PersonType
import hashlib


class EmployeeRepository(BaseRepository):
    """Repository for Employee CRUD operations"""
    
    def get_all(self, department_id=None, supervisor_id=None, 
                person_type=None, is_active=None, search_term=None):
        """
        Get employees with optional filters.
        
        Args:
            department_id: Filter by department
            supervisor_id: Filter by supervisor (for supervisors viewing their team)
            person_type: Filter by PersonType enum or string
            is_active: Filter by active status
            search_term: Search in name or email
            
        Returns:
            list: List of employee dicts
        """
        query = """
            SELECT 
                p.person_id, p.name, p.email, p.person_type,
                d.department_name, p.phone, p.is_active,
                s.name AS supervisor_name,
                CASE 
                    WHEN p.person_type = 'HOD' THEN h.fixed_salary
                    WHEN p.person_type = 'SUPERVISOR' THEN sup.fixed_salary
                    WHEN p.person_type = 'SALESMAN' THEN sm.hourly_rate
                    WHEN p.person_type = 'GENERAL_EMPLOYEE' THEN ge.hourly_rate
                END as salary_rate
            FROM person p
            LEFT JOIN departments d ON p.department_id = d.department_id
            LEFT JOIN hod h ON p.person_id = h.person_id
            LEFT JOIN supervisor sup ON p.person_id = sup.person_id
            LEFT JOIN salesman sm ON p.person_id = sm.person_id
            LEFT JOIN general_employee ge ON p.person_id = ge.person_id
            LEFT JOIN emp_supervisor es ON p.person_id = es.employee_id
            LEFT JOIN person s ON es.supervisor_id = s.person_id
            WHERE 1=1
        """
        params = []
        
        if department_id:
            query += " AND p.department_id = %s"
            params.append(department_id)
        
        if supervisor_id:
            query += " AND es.supervisor_id = %s"
            params.append(supervisor_id)
        
        if person_type:
            type_value = person_type.value if isinstance(person_type, PersonType) else person_type
            query += " AND p.person_type = %s"
            params.append(type_value)
        
        if is_active is not None:
            query += " AND p.is_active = %s"
            params.append(is_active)
        
        if search_term:
            query += " AND (p.name LIKE %s OR p.email LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        query += " ORDER BY p.person_type, p.name"
        
        return self.execute_query(query, params)
    
    def get_by_id(self, person_id):
        """
        Get single employee by ID with all details.
        
        Args:
            person_id: Employee ID
            
        Returns:
            dict or None: Employee data
        """
        query = """
            SELECT 
                p.*,
                h.fixed_salary AS hod_salary,
                sup.fixed_salary AS supervisor_salary,
                sm.hourly_rate AS salesman_hourly,
                sm.commission_rate,
                ge.hourly_rate AS ge_hourly,
                es.supervisor_id,
                s.name AS supervisor_name
            FROM person p
            LEFT JOIN hod h ON p.person_id = h.person_id
            LEFT JOIN supervisor sup ON p.person_id = sup.person_id
            LEFT JOIN salesman sm ON p.person_id = sm.person_id
            LEFT JOIN general_employee ge ON p.person_id = ge.person_id
            LEFT JOIN emp_supervisor es ON p.person_id = es.employee_id
            LEFT JOIN person s ON es.supervisor_id = s.person_id
            WHERE p.person_id = %s
        """
        return self.execute_query(query, (person_id,), fetch_one=True)
    
    def get_by_email(self, email):
        """Get employee by email address."""
        query = "SELECT * FROM person WHERE email = %s"
        return self.execute_query(query, (email,), fetch_one=True)
    
    def deactivate(self, person_id):
        """
        Soft delete - deactivate employee.
        
        Args:
            person_id: Employee ID
            
        Returns:
            int: Affected rows
        """
        return self.execute_write(
            "UPDATE person SET is_active = FALSE WHERE person_id = %s",
            (person_id,)
        )
    
    def activate(self, person_id):
        """Reactivate a deactivated employee."""
        return self.execute_write(
            "UPDATE person SET is_active = TRUE WHERE person_id = %s",
            (person_id,)
        )
    
    def get_count(self, department_id=None, is_active=True):
        """
        Get employee count.
        
        Args:
            department_id: Optional department filter
            is_active: Filter by active status
            
        Returns:
            int: Employee count
        """
        where_parts = ["is_active = %s"]
        params = [is_active]
        
        if department_id:
            where_parts.append("department_id = %s")
            params.append(department_id)
        
        return super().get_count("person", " AND ".join(where_parts), params)
    
    def get_supervisors(self):
        """Get all active supervisors for dropdown."""
        query = """
            SELECT p.person_id, p.name 
            FROM person p
            JOIN supervisor s ON p.person_id = s.person_id
            WHERE p.is_active = TRUE
            ORDER BY p.name
        """
        return self.execute_query(query)
    
    def get_salesmen(self):
        """Get all active salesmen for dropdown."""
        query = """
            SELECT p.person_id, p.name 
            FROM person p
            JOIN salesman s ON p.person_id = s.person_id
            WHERE p.is_active = TRUE
            ORDER BY p.name
        """
        return self.execute_query(query)
    
    def get_hods(self):
        """Get all active HODs for dropdown."""
        query = """
            SELECT p.person_id, p.name 
            FROM person p
            JOIN hod h ON p.person_id = h.person_id
            WHERE p.is_active = TRUE
            ORDER BY p.name
        """
        return self.execute_query(query)
