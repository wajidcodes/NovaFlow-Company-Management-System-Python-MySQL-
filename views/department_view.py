"""
Department View - Manages department UI interactions
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView
from models.department_repository import DepartmentRepository
from config.database import get_db_connection

class DepartmentView(BaseView):
    def create_ui(self):
        self.repository = DepartmentRepository()
        self.search_var = tk.StringVar()
        self.tree = None 
        
        # Header
        self.create_header("🏢 Departments Management", "#4f46e5")
        
        # Toolbar
        self.create_toolbar()
        
        # Treeview
        self.create_treeview()
        
        # Load initial data
        self.load_data()
        
    def create_toolbar(self):
        """Create search and action buttons"""
        toolbar = tk.Frame(self.frame, bg='white')
        toolbar.pack(fill='x', padx=20, pady=10)
        
        # Search
        search_frame = tk.Frame(toolbar, bg='white')
        search_frame.pack(side='left')
        
        tk.Label(search_frame, text="🔍", font=('Arial', 14), bg='white').pack(side='left', padx=(0, 5))
        
        self.search_var.trace('w', lambda *args: self.load_data())
        tk.Entry(search_frame, textvariable=self.search_var,
                 font=('Arial', 10), bg='#f8fafc', width=30, relief='solid', bd=1).pack(side='left', ipady=5)
        
        # Actions
        btn_frame = tk.Frame(toolbar, bg='white')
        btn_frame.pack(side='right')
        
        if self.current_user['person_type'] == 'HOD':
            self.create_button(btn_frame, "➕ Add", self.add_department, "#10b981")
            self.create_button(btn_frame, "✏️ Edit", self.edit_department, "#3b82f6")
            self.create_button(btn_frame, "🗑️ Delete", self.delete_department, "#ef4444")
            
        self.create_button(btn_frame, "🔄 Refresh", self.load_data, "#6b7280")
        
    def create_treeview(self):
        """Create the departments table"""
        columns = ('ID', 'Department Name', 'Location', 'HOD', 'Employee Count')
        # Fix: Use super().create_treeview instead of missing create_table
        self.tree = super().create_treeview(columns)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Department Name', text='Department Name')
        self.tree.heading('Location', text='Location')
        self.tree.heading('HOD', text='Head of Department')
        self.tree.heading('Employee Count', text='Employees')
        
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Department Name', width=200)
        self.tree.column('Location', width=200)
        self.tree.column('HOD', width=200)
        self.tree.column('Employee Count', width=100, anchor='center')
        
        self.tree.bind('<Double-1>', lambda e: self.edit_department())

    def load_data(self):
        """Fetch and display departments"""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            departments = self.repository.get_all(search_term=self.search_var.get())
            
            for dept in departments:
                self.tree.insert('', 'end', values=(
                    dept['department_id'],
                    dept['department_name'],
                    dept['location_name'] or 'N/A',
                    dept['hod_name'] or 'Not Assigned',
                    dept['employee_count']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load departments: {e}")

    def add_department(self):
        from dialogs.department_dialog import DepartmentDialog
        dialog = DepartmentDialog(self.root, mode='add', db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            self.load_data()

    def edit_department(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a department.")
            return
            
        dept_id = self.tree.item(selected[0])['values'][0]
        dept = self.repository.get_by_id(dept_id)
        
        if dept:
            from dialogs.department_dialog import DepartmentDialog
            dialog = DepartmentDialog(self.root, mode='edit', 
                                    department_data=dict(dept), 
                                    db_connection_func=get_db_connection)
            self.root.wait_window(dialog.dialog)
            if dialog.result:
                self.load_data()

    def delete_department(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a department.")
            return
            
        item = self.tree.item(selected[0])
        dept_id = item['values'][0]
        emp_count = item['values'][4]
        
        if emp_count > 0:
            messagebox.showerror("Error", "Cannot delete department with employees.")
            return
            
        if messagebox.askyesno("Confirm", "Delete this department?"):
            self.repository.delete(dept_id)
            self.load_data()
