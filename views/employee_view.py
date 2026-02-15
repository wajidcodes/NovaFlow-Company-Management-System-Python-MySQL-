"""
Employee Management View
"""
import tkinter as tk
from tkinter import messagebox
from views.base_view import BaseView
from models.employee_repository import EmployeeRepository
from dialogs.employee_dialog import EmployeeDialog
from utils.constants import PersonType, has_permission, COLORS
from config.database import get_db_connection  # For passing to dialog

class EmployeeView(BaseView):
    def create_ui(self):
        self.repo = EmployeeRepository()
        
        # Header
        if has_permission(self.current_user, 'manage_employees'):
            self.create_header("👥 Employee Management", "➕ Add Employee", self.add_employee)
        else:
            self.create_header("👥 Employees")
            
        # Toolbar
        filter_options = []
        # Role filter
        roles = ['All Roles', 'HOD', 'SUPERVISOR', 'SALESMAN', 'GENERAL_EMPLOYEE']
        filter_options.append(('Role:', roles, self.refresh_data))
        
        # Status filter
        statuses = ['Active', 'Inactive', 'All']
        filter_options.append(('Status:', statuses, self.refresh_data))
        
        self.widgets = self.create_toolbar(self.refresh_data, filter_options)
        
        # Treeview
        columns = ('ID', 'Name', 'Role', 'Department', 'Email', 'Phone', 'Status', 'Supervisor')
        self.tree = self.create_treeview(columns)
        
        # Configure column widths
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Name', width=150)
        self.tree.column('Role', width=120)
        self.tree.column('Department', width=120)
        self.tree.column('Email', width=200)
        self.tree.column('Status', width=80, anchor='center')
        
        # Events
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Load initial data
        self.refresh_data()
        
    def refresh_data(self):
        """Refresh employee list based on filters"""
        # Get filters
        search = self.widgets['search_var'].get().strip()
        role_filter = self.widgets['filter_Role:'].get()
        status_filter = self.widgets['filter_Status:'].get()
        
        # Process filters
        person_type = None if role_filter == 'All Roles' else role_filter
        
        is_active = None
        if status_filter == 'Active':
            is_active = True
        elif status_filter == 'Inactive':
            is_active = False
            
        # Context filters based on logged in user
        dept_id = None
        sup_id = None
        
        user_type = PersonType(self.current_user['person_type'])
        
        if user_type == PersonType.HOD:
            dept_id = self.current_user['department_id']
        elif user_type == PersonType.SUPERVISOR:
            sup_id = self.current_user['person_id']
            
        # Fetch data
        try:
            employees = self.repo.get_all(
                department_id=dept_id,
                supervisor_id=sup_id,
                person_type=person_type,
                is_active=is_active,
                search_term=search
            )
            
            # Clear tree
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Populate tree
            for emp in employees:
                status_display = "Active" if emp['is_active'] else "Inactive"
                tag = 'active' if emp['is_active'] else 'inactive'
                
                self.tree.insert('', 'end', values=(
                    emp['person_id'],
                    emp['name'],
                    emp['person_type'],
                    emp['department_name'] or '-',
                    emp['email'],
                    emp['phone'],
                    status_display,
                    emp['supervisor_name'] or '-'
                ), tags=(tag,))
                
        except Exception as e:
            self.show_error(f"Failed to load employees: {e}")
            
    def add_employee(self):
        """Open add employee dialog"""
        dialog = EmployeeDialog(self.root, mode='add', 
                               current_user=self.current_user,
                               db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.refresh_data()
            self.show_success("Employee added successfully")
            
    def on_double_click(self, event):
        """Handle edit on double click"""
        if not has_permission(self.current_user, 'manage_employees'):
            return
            
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        person_id = item['values'][0]
        
        try:
            # Fetch full details
            employee_data = self.repo.get_by_id(person_id)
            
            if employee_data:
                dialog = EmployeeDialog(self.root, mode='edit', 
                                       employee_data=employee_data,
                                       current_user=self.current_user,
                                       db_connection_func=get_db_connection)
                self.root.wait_window(dialog.dialog)
                
                if dialog.result:
                    self.refresh_data()
                    
        except Exception as e:
            self.show_error(f"Failed to load employee details: {e}")
