"""
Order View - Manages order UI interactions
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView
from models.order_repository import OrderRepository
from config.database import get_db_connection

class OrderView(BaseView):
    def create_ui(self):
        self.repository = OrderRepository()
        self.search_var = tk.StringVar()
        self.status_filter = None

        self.create_header("🧾 Orders Management", "#4f46e5")
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

        tk.Label(toolbar, text="Status:", bg='white').pack(side='left', padx=(20, 5))
        self.status_filter = ttk.Combobox(toolbar, values=['All', 'PENDING', 'PROCESSING', 'COMPLETED', 'CANCELLED'], state='readonly')
        self.status_filter.current(0)
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_data())
        self.status_filter.pack(side='left')

        btn_frame = tk.Frame(toolbar, bg='white')
        btn_frame.pack(side='right')
        
        if self.current_user['person_type'] in ['SALESMAN', 'HOD']:
            self.create_button(btn_frame, "➕ New Order", self.add_order, "#10b981")
            self.create_button(btn_frame, "✏️ View/Edit", self.edit_order, "#3b82f6")
            if self.current_user['person_type'] == 'HOD':
                self.create_button(btn_frame, "🗑️ Delete", self.delete_order, "#ef4444")
            
        self.create_button(btn_frame, "🔄 Refresh", self.load_data, "#6b7280")

    def create_treeview(self):
        columns = ('ID', 'Date', 'Customer', 'Salesman', 'Total', 'Status')
        self.tree = self.create_treeview_widget(columns)
        
        self.tree.heading('ID', text='Order ID')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Customer', text='Customer')
        self.tree.heading('Salesman', text='Salesman')
        self.tree.heading('Total', text='Total Amount')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('ID', width=70, anchor='center')
        self.tree.column('Total', anchor='e')
        
        self.tree.tag_configure('PENDING', background='#fef3c7')
        self.tree.tag_configure('COMPLETED', background='#d1fae5')
        self.tree.tag_configure('CANCELLED', background='#fee2e2')
        
        self.tree.bind('<Double-1>', lambda e: self.edit_order())

    def create_treeview_widget(self, columns):
        # Helper to bridge the mismatch if BaseView uses create_treeview
        return super().create_treeview(columns)

    def load_data(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            sid = self.current_user['person_id'] if self.current_user['person_type'] == 'SALESMAN' else None
            status = self.status_filter.get()
            
            orders = self.repository.get_all(
                salesman_id=sid,
                status=status,
                search_term=self.search_var.get()
            )
            
            for ord in orders:
                self.tree.insert('', 'end', values=(
                    ord['order_id'], ord['order_date'], ord['customer_name'],
                    ord['salesman_name'], f"${ord['total_amount']:.2f}", ord['status']
                ), tags=(ord['status'],))
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_order(self):
        from dialogs.order_dialog import OrderDialog
        dialog = OrderDialog(self.root, mode='add', current_user=self.current_user, db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        if dialog.result: self.load_data()

    def edit_order(self):
        sel = self.tree.selection()
        if not sel: return
        
        oid = self.tree.item(sel[0])['values'][0]
        data = self.repository.get_by_id(oid)
        
        from dialogs.order_dialog import OrderDialog
        dialog = OrderDialog(self.root, mode='edit', order_data=dict(data), current_user=self.current_user, db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        if dialog.result: self.load_data()

    def delete_order(self):
        sel = self.tree.selection()
        if not sel: return
        
        oid = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Delete Order #{oid}? Stock will be returned."):
            # Need to implement the complex return stock logic here or in repository
            # Main.py had this logic inline. It's better to move it to a service layer, 
            # but for now we'll rely on the repository delete (which I implemented to just delete).
            # WAIT: My repository delete() DOES NOT handle stock return yet. 
            # I should fix the repository or the view.
            # Best is to put business logic in a Service, but we are doing Repo+View.
            # Let's fix the delete logic here using a quick inline DB call like main.py did, 
            # or better yet update the repository to handle it.
            # I'll update the repository to handle cascading and restoration in a transaction if possible,
            # but for now I will mirror the main.py logic here to ensure safety.
            
            try:
                # Mirroring logic from main.py
                conn = get_db_connection()
                cur = conn.cursor()
                
                # Restore stock
                cur.execute("SELECT warehouse_id, product_id, qty FROM order_items WHERE order_id = %s", (oid,))
                items = cur.fetchall()
                for i in items:
                    cur.execute("UPDATE warehouse_products SET qty = qty + %s WHERE warehouse_id = %s AND product_id = %s", 
                               (i['qty'], i['warehouse_id'], i['product_id']))
                
                conn.commit()
                conn.close()
                
                # Now delete
                self.repository.delete_order(oid)
                self.load_data()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
