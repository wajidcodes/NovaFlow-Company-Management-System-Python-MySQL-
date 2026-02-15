"""
WorkLog Repository - Data access for work logs
"""
from models.base_repository import BaseRepository
from utils.constants import ApprovalStatus

class WorkLogRepository(BaseRepository):
    """Repository for WorkLog CRUD operations"""
    
    def get_all(self, emp_id=None, supervisor_id=None, hod_id=None, 
                status_filter=None, search_term=None):
        """
        Get work logs with complex role-based filtering.
        
        Args:
            emp_id: View own logs
            supervisor_id: View logs of supervisees
            hod_id: View logs of department
            status_filter: Filter by approval status
            search_term: Search employee name or project
            
        Returns:
            list: List of work log dicts
        """
        query = """
            SELECT 
                w.log_id, w.work_date, w.total_hours AS hours_worked, w.notes AS description,
                w.supervisor_approved, w.hod_approved, w.approval_status,
                e.name AS employee_name,
                p.project_name,
                sup.name AS supervisor_name,
                hod.name AS hod_name
            FROM work_log w
            JOIN person e ON w.employee_id = e.person_id
            LEFT JOIN projects p ON w.project_id = p.project_id
            LEFT JOIN emp_supervisor es ON w.employee_id = es.employee_id
            LEFT JOIN person sup ON es.supervisor_id = sup.person_id
            LEFT JOIN departments d ON e.department_id = d.department_id
            LEFT JOIN person hod ON d.hod_id = hod.person_id
            WHERE 1=1
        """
        params = []
        
        # Access Control Logic
        if emp_id:
            # Employee sees their own
            query += " AND w.employee_id = %s"
            params.append(emp_id)
        elif supervisor_id:
            # Supervisor sees their team's logs
            query += " AND es.supervisor_id = %s"
            params.append(supervisor_id)
        elif hod_id:
            # HOD sees department's logs
            query += " AND e.department_id = (SELECT department_id FROM person WHERE person_id = %s)"
            params.append(hod_id)
            
        # Status Filter
        if status_filter:
            status_val = status_filter.value if hasattr(status_filter, 'value') else status_filter
            if status_val == 'Pending':
                query += " AND w.approval_status = 'PENDING'"
            elif status_val == 'Approved':
                query += " AND w.approval_status = 'APPROVED'"
            elif status_val == 'Rejected':
                query += " AND w.approval_status = 'REJECTED'"
        
        # Search
        if search_term:
            query += " AND (e.name LIKE %s OR p.project_name LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
            
        query += " ORDER BY w.work_date DESC"
        
        return self.execute_query(query, params)
    
    def create(self, employee_id, project_id, date, hours, description):
        """Create work log"""
        query = """
            INSERT INTO work_log (employee_id, project_id, work_date, total_hours, notes, approval_status)
            VALUES (%s, %s, %s, %s, %s, 'PENDING')
        """
        return self.execute_write(query, (employee_id, project_id, date, hours, description))
    
    def update_status(self, log_id, supervisor_approved=None, hod_approved=None, status=None):
        """Update approval status"""
        updates = []
        params = []
        
        if supervisor_approved is not None:
            updates.append("supervisor_approved = %s")
            params.append(supervisor_approved)
            
        if hod_approved is not None:
            updates.append("hod_approved = %s")
            params.append(hod_approved)
            
        if status:
            updates.append("approval_status = %s")
            params.append(status)
            
        if not updates:
            return 0
            
        params.append(log_id)
        query = f"UPDATE work_log SET {', '.join(updates)} WHERE log_id = %s"
        
        return self.execute_write(query, params)
