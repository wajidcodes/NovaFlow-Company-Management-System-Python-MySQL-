"""
Customer View - Manages customer UI interactions
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView
from models.customer_repository import CustomerRepository
from config.database import get_db_connection

class CustomerView(BaseView):
    def create_ui(self):
        self.repository = CustomerRepository()
        self.search_var = tk.StringVar()

        self.create_header("👥 Customer Management", "#0891b2")
        self.create_toolbar()
        self.create_treeview()
        self.load_data()

    def create_toolbar(self):
        toolbar = tk.Frame(self.frame, bg='white')
        toolbar.pack(fill='x', padx=20, pady=10)
        
        search_frame = tk.Frame(toolbar, bg='white')
        search_frame.pack(side='left')
        tk.Label(search_frame, text="🔍", font=('Arial', 14), bg='white').pack(side='left')
        
        self.search_var.trace('w', lambda *args: self.load_data())
        tk.Entry(search_frame, textvariable=self.search_var, bg='#f8fafc', relief='solid', bd=1).pack(side='left')

        btn_frame = tk.Frame(toolbar, bg='white')
        btn_frame.pack(side='right')
        
        if self.current_user['person_type'] in ['SALESMAN', 'HOD']:
            self.create_button(btn_frame, "➕ Add", self.add_customer, "#10b981")
            self.create_button(btn_frame, "✏️ Edit", self.edit_customer, "#3b82f6")
            self.create_button(btn_frame, "🗑️ Delete", self.delete_customer, "#ef4444")
            
        self.create_button(btn_frame, "🔄 Refresh", self.load_data, "#6b7280")

    def create_treeview(self):
        columns = ('ID', 'Name', 'Email', 'Phone', 'Salesman', 'Orders')
        self.tree = super().create_treeview(columns)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Customer Name')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Phone', text='Phone')
        self.tree.heading('Salesman', text='Assigned To')
        self.tree.heading('Orders', text='Total Orders')
        
        self.tree.column('ID', width=50, anchor='center')
        
        self.tree.tag_configure('my_customer', background='#ecfeff')
        
        self.tree.bind('<Double-1>', lambda e: self.edit_customer())

    def load_data(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Salesman typically sees everyone but highlights his own - logic from main.py
            customers = self.repository.get_all(search_term=self.search_var.get())
            
            my_id = self.current_user['person_id']
            
            for cust in customers:
                tag = 'my_customer' if cust['salesman_id'] == my_id else ''
                self.tree.insert('', 'end', values=(
                    cust['customer_id'], cust['name'], cust['email'] or '-',
                    cust['phone'] or '-', cust['salesman_name'] or 'Unassigned', cust['order_count']
                ), tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_customer(self):
        from dialogs.customer_dialog import CustomerDialog
        dialog = CustomerDialog(self.root, mode='add', current_user=self.current_user, db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        if dialog.result: self.load_data()

    def edit_customer(self):
        sel = self.tree.selection()
        if not sel: return
        
        cid = self.tree.item(sel[0])['values'][0]
        data = self.repository.get_by_id(cid)
        
        from dialogs.customer_dialog import CustomerDialog
        dialog = CustomerDialog(self.root, mode='edit', customer_data=dict(data), current_user=self.current_user, db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        if dialog.result: self.load_data()

    def delete_customer(self):
        sel = self.tree.selection()
        if not sel: return
        
        item = self.tree.item(sel[0])
        cid = item['values'][0]
        orders = item['values'][5]
        
        if orders > 0:
            messagebox.showerror("Error", "Cannot delete customer with orders.")
            return

        if messagebox.askyesno("Confirm", "Delete customer?"):
            self.repository.delete(cid)
            self.load_data()
