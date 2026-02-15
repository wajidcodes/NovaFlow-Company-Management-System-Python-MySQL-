"""
Work Log View - Manages Work Log UI interactions
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView
from models.worklog_repository import WorkLogRepository
from config.database import get_db_connection
from utils.constants import COLORS

class WorkLogView(BaseView):
    def create_ui(self):
        self.repository = WorkLogRepository()
        self.search_var = tk.StringVar()
        self.status_filter = None

        self.create_header("⏰ Work Logs", "#f59e0b")
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
        self.status_filter = ttk.Combobox(toolbar, values=['All', 'PENDING', 'APPROVED', 'REJECTED'], state='readonly')
        self.status_filter.current(0)
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_data())
        self.status_filter.pack(side='left')

        # Buttons
        btn_frame = tk.Frame(toolbar, bg='white')
        btn_frame.pack(side='right')
        
        if self.current_user['person_type'] in ['GENERAL_EMPLOYEE', 'SALESMAN']:
            self.create_button(btn_frame, "➕ Log Work", self.add_log, "#10b981")
            
        if self.current_user['person_type'] in ['SUPERVISOR', 'HOD']:
             self.create_button(btn_frame, "✅ Approve", self.approve_log, "#3b82f6")
             self.create_button(btn_frame, "❌ Reject", self.reject_log, "#ef4444")

        self.create_button(btn_frame, "🔄 Refresh", self.load_data, "#6b7280")

    def create_treeview(self):
        columns = ('ID', 'Employee', 'Date', 'Hours', 'Status', 'Description')
        self.tree = super().create_treeview(columns)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Employee', text='Employee')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Hours', text='Hours')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Description', text='Description')
        
        self.tree.column('ID', width=50, anchor='center')
        
        self.tree.tag_configure('PENDING', background='#fef3c7')
        self.tree.tag_configure('APPROVED', background='#d1fae5')
        self.tree.tag_configure('REJECTED', background='#fee2e2')

    def load_data(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Context filters
            emp_id = None
            hod_id = None
            
            if self.current_user['person_type'] in ['GENERAL_EMPLOYEE', 'SALESMAN']:
                emp_id = self.current_user['person_id']
            elif self.current_user['person_type'] == 'HOD':
                # HOD sees dept logs
                hod_id = self.current_user['person_id']
            # Supervisor logic would go here if needed (supervisor_id)
            
            status = self.status_filter.get()
            
            logs = self.repository.get_all(
                emp_id=emp_id,
                hod_id=hod_id,
                status_filter=status,
                search_term=self.search_var.get()
            )
            
            for log in logs:
                self.tree.insert('', 'end', values=(
                    log['log_id'], log['employee_name'], log['work_date'], 
                    log['hours_worked'], log['approval_status'], log['description'] or ''
                ), tags=(log['approval_status'],))
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_log(self):
        from dialogs.worklog_dialog import WorkLogDialog
        dialog = WorkLogDialog(self.root, mode='add', current_user=self.current_user, db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        if dialog.result: self.load_data()

    def approve_log(self):
        self.update_status('APPROVED')

    def reject_log(self):
        self.update_status('REJECTED')

    def update_status(self, new_status):
        sel = self.tree.selection()
        if not sel: return
        
        log_id = self.tree.item(sel[0])['values'][0]
        
        if messagebox.askyesno("Confirm", f"Mark log #{log_id} as {new_status}?"):
            try:
                # Determine approval flags based on role
                sup_approve = None
                hod_approve = None
                
                is_approved_bool = 1 if new_status == 'APPROVED' else 0
                
                # Check role using checking logic consistent with create_toolbar
                role = self.current_user.get('person_type', '')
                
                if role == 'SUPERVISOR':
                    sup_approve = is_approved_bool
                elif role == 'HOD':
                    hod_approve = is_approved_bool
                
                # Update database
                self.repository.update_status(
                    log_id, 
                    supervisor_approved=sup_approve, 
                    hod_approved=hod_approve, 
                    status=new_status
                )
                
                self.load_data()
                messagebox.showinfo("Success", f"Log marked as {new_status}")
                
            except Exception as e:
                 messagebox.showerror("Update Error", f"Failed to update status: {e}")
