"""
Project View - Manages project UI interactions
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView
from models.project_repository import ProjectRepository
from config.database import get_db_connection

class ProjectView(BaseView):
    def create_ui(self):
        self.repository = ProjectRepository()
        self.search_var = tk.StringVar()
        self.status_filter = None

        self.create_header("📋 Projects Management", "#8b5cf6")
        self.create_toolbar()
        self.create_treeview()
        self.load_data()

    def create_toolbar(self):
        toolbar = tk.Frame(self.frame, bg='white')
        toolbar.pack(fill='x', padx=20, pady=10)
        
        # Search
        search_frame = tk.Frame(toolbar, bg='white')
        search_frame.pack(side='left')
        tk.Label(search_frame, text="🔍", font=('Arial', 14), bg='white').pack(side='left')
        
        self.search_var.trace('w', lambda *args: self.load_data())
        tk.Entry(search_frame, textvariable=self.search_var, bg='#f8fafc', relief='solid', bd=1).pack(side='left')

        # Filter
        tk.Label(toolbar, text="Status:", bg='white').pack(side='left', padx=(20, 5))
        self.status_filter = ttk.Combobox(toolbar, values=['All', 'PLANNING', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD'], state='readonly')
        self.status_filter.current(0)
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_data())
        self.status_filter.pack(side='left')

        # Buttons
        btn_frame = tk.Frame(toolbar, bg='white')
        btn_frame.pack(side='right')
        
        if self.current_user['person_type'] == 'HOD':
            self.create_button(btn_frame, "➕ Add", self.add_project, "#10b981")
            self.create_button(btn_frame, "✏️ Edit", self.edit_project, "#3b82f6")
            self.create_button(btn_frame, "🗑️ Delete", self.delete_project, "#ef4444")
            
        self.create_button(btn_frame, "🔄 Refresh", self.load_data, "#6b7280")

    def create_treeview(self):
        columns = ('ID', 'Project Name', 'Department', 'Location', 'Status', 'Start Date', 'End Date')
        # Use super().create_treeview directly as it returns the tree
        self.tree = super().create_treeview(columns)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Project Name', text='Project Name')
        self.tree.heading('Department', text='Department')
        self.tree.heading('Location', text='Location')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Start Date', text='Start Date')
        self.tree.heading('End Date', text='End Date')
        
        self.tree.column('ID', width=50, anchor='center')
        
        self.tree.tag_configure('PLANNING', background='#fef3c7')
        self.tree.tag_configure('IN_PROGRESS', background='#dbeafe')
        self.tree.tag_configure('COMPLETED', background='#d1fae5')
        self.tree.tag_configure('ON_HOLD', background='#fee2e2')
        
        self.tree.bind('<Double-1>', lambda e: self.edit_project())

    def load_data(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            dept_id = self.current_user['department_id'] if self.current_user['person_type'] == 'HOD' else None
            status = self.status_filter.get()
            
            projects = self.repository.get_all(
                department_id=dept_id,
                status=status,
                search_term=self.search_var.get()
            )
            
            for p in projects:
                self.tree.insert('', 'end', values=(
                    p['project_id'], p['project_name'], p['department_name'],
                    p['location_name'], p['status'], p['start_date'], p['end_date']
                ), tags=(p['status'],))
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_project(self):
        from dialogs.project_dialog import ProjectDialog
        dialog = ProjectDialog(self.root, mode='add', current_user=self.current_user, db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        if dialog.result: self.load_data()

    def edit_project(self):
        sel = self.tree.selection()
        if not sel: return
        
        pid = self.tree.item(sel[0])['values'][0]
        data = self.repository.get_by_id(pid)
        
        from dialogs.project_dialog import ProjectDialog
        dialog = ProjectDialog(self.root, mode='edit', project_data=dict(data), current_user=self.current_user, db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        if dialog.result: self.load_data()

    def delete_project(self):
        sel = self.tree.selection()
        if not sel: return
        
        pid = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete project?"):
            self.repository.delete(pid)
            self.load_data()
