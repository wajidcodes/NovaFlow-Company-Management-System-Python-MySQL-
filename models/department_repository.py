"""
Department Repository - Data access for department operations
"""
from models.base_repository import BaseRepository

class DepartmentRepository(BaseRepository):
    """Repository for Department CRUD operations"""
    
    def get_all(self, search_term=None):
        """
        Get all departments with optional search.
        
        Args:
            search_term: Search in name or location
            
        Returns:
            list: List of department dicts
        """
        query = """
            SELECT 
                d.department_id,
                d.department_name,
                l.location_name,
                p.name AS hod_name,
                d.hod_id,
                d.location_id,
                COUNT(DISTINCT e.person_id) AS employee_count
            FROM departments d
            LEFT JOIN locations l ON d.location_id = l.location_id
            LEFT JOIN person p ON d.hod_id = p.person_id
            LEFT JOIN person e ON d.department_id = e.department_id AND e.is_active = TRUE
            WHERE 1=1
        """
        params = []
        
        if search_term:
            query += " AND (d.department_name LIKE %s OR l.location_name LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        query += " GROUP BY d.department_id ORDER BY d.department_name"
        
        return self.execute_query(query, params)
    
    def get_by_id(self, dept_id):
        """Get single department by ID"""
        query = """
            SELECT department_id, department_name, location_id, hod_id
            FROM departments
            WHERE department_id = %s
        """
        return self.execute_query(query, (dept_id,), fetch_one=True)
    
    def create(self, name, location_id, hod_id):
        """Create new department"""
        query = """
            INSERT INTO departments (department_name, location_id, hod_id)
            VALUES (%s, %s, %s)
        """
        return self.execute_write(query, (name, location_id, hod_id))
    
    def update(self, dept_id, name, location_id, hod_id):
        """Update department"""
        query = """
            UPDATE departments 
            SET department_name = %s, location_id = %s, hod_id = %s
            WHERE department_id = %s
        """
        return self.execute_write(query, (name, location_id, hod_id, dept_id))
    
    def delete(self, dept_id):
        """Delete department"""
        return self.execute_write("DELETE FROM departments WHERE department_id = %s", (dept_id,))
    
    def get_locations(self):
        """Get all locations for dropdown"""
        return self.execute_query("SELECT * FROM locations ORDER BY location_name")
