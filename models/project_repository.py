"""
Project Repository - Data access for project operations
"""
from models.base_repository import BaseRepository
from utils.constants import ProjectStatus

class ProjectRepository(BaseRepository):
    """Repository for Project CRUD operations"""
    
    def get_all(self, department_id=None, status=None, search_term=None):
        """
        Get projects with filters.
        
        Args:
            department_id: Filter by department
            status: Filter by status (ProjectStatus enum or string)
            search_term: Search in project name
            
        Returns:
            list: List of project dicts
        """
        query = """
            SELECT 
                p.project_id,
                p.project_name,
                d.department_name,
                l.location_name,
                p.status,
                p.start_date,
                p.end_date
            FROM projects p
            LEFT JOIN departments d ON p.department_id = d.department_id
            LEFT JOIN locations l ON p.location_id = l.location_id
            WHERE 1=1
        """
        params = []
        
        if department_id:
            query += " AND p.department_id = %s"
            params.append(department_id)
        
        if status:
            status_val = status.value if hasattr(status, 'value') else status
            # Only add filter if it's a valid status (not 'All')
            if status_val != 'All':
                query += " AND p.status = %s"
                params.append(status_val)
        
        if search_term:
            query += " AND p.project_name LIKE %s"
            params.append(f"%{search_term}%")
        
        query += " ORDER BY p.project_name"
        
        return self.execute_query(query, params)
    
    def get_by_id(self, project_id):
        """Get project by ID"""
        query = """
            SELECT project_id, project_name, department_id, location_id, 
                   status, start_date, end_date
            FROM projects
            WHERE project_id = %s
        """
        return self.execute_query(query, (project_id,), fetch_one=True)
    
    def create(self, name, dept_id, loc_id, status, start_date, end_date):
        """Create new project"""
        query = """
            INSERT INTO projects (project_name, department_id, location_id, status, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.execute_write(query, (name, dept_id, loc_id, status, start_date, end_date))
    
    def update(self, project_id, name, dept_id, loc_id, status, start_date, end_date):
        """Update project"""
        query = """
            UPDATE projects 
            SET project_name = %s, department_id = %s, location_id = %s, 
                status = %s, start_date = %s, end_date = %s
            WHERE project_id = %s
        """
        return self.execute_write(query, (
            name, dept_id, loc_id, status, start_date, end_date, project_id
        ))
    
    def delete(self, project_id):
        """Delete project"""
        return self.execute_write("DELETE FROM projects WHERE project_id = %s", (project_id,))
