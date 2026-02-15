"""
Product View - Manages product UI interactions
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView
from models.product_repository import ProductRepository
from config.database import get_db_connection

class ProductView(BaseView):
    def create_ui(self):
        self.repository = ProductRepository()
        self.search_var = tk.StringVar()

        self.create_header("📦 Products Inventory", "#059669")
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

        # Buttons
        btn_frame = tk.Frame(toolbar, bg='white')
        btn_frame.pack(side='right')
        
        if self.current_user['person_type'] in ['SUPERVISOR', 'HOD']:
            self.create_button(btn_frame, "➕ Add", self.add_product, "#10b981")
            self.create_button(btn_frame, "✏️ Edit", self.edit_product, "#3b82f6")
            self.create_button(btn_frame, "🗑️ Delete", self.delete_product, "#ef4444")
            
        self.create_button(btn_frame, "🔄 Refresh", self.load_data, "#6b7280")

    def create_treeview(self):
        columns = ('ID', 'Product Name', 'Type', 'Price', 'Warehouse', 'Stock', 'Low Stock')
        self.tree = super().create_treeview(columns)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Product Name', text='Product Name')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Price', text='Price ($)')
        self.tree.heading('Warehouse', text='Warehouse')
        self.tree.heading('Stock', text='Stock Qty')
        self.tree.heading('Low Stock', text='Status')
        
        self.tree.column('ID', width=50, anchor='center')
        
        self.tree.tag_configure('low_stock', background='#fee2e2', foreground='#dc2626')
        self.tree.tag_configure('normal', background='white')
        
        self.tree.bind('<Double-1>', lambda e: self.edit_product())

    def load_data(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            sup_id = self.current_user['person_id'] if self.current_user['person_type'] == 'SUPERVISOR' else None
            
            products = self.repository.get_all(
                supervisor_id=sup_id,
                search_term=self.search_var.get()
            )
            
            for prod in products:
                is_low = prod['qty'] <= (prod['reorder_level'] or 10)
                tag = 'low_stock' if is_low else 'normal'
                status = '⚠️ Low Stock' if is_low else '✅ OK'
                
                self.tree.insert('', 'end', values=(
                    prod['product_id'], prod['product_name'], prod['product_type'] or '-',
                    f"{prod['unit_price']:.2f}", prod['warehouse_name'], prod['qty'], status,
                    # Hidden column logic is handled by repository call in edit
                ), tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_product(self):
        from dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self.root, mode='add', current_user=self.current_user, db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        if dialog.result: self.load_data()

    def edit_product(self):
        sel = self.tree.selection()
        if not sel: return
        
        item = self.tree.item(sel[0])
        prod_id = item['values'][0]
        # In this view, we can infer warehouse from the row, but repository needs ID.
        # Since treeview values doesn't have warehouse_id, we might need to fetch it differently or add hidden col.
        # Actually `edit_product` in main.py used warehouse_name to look it up.
        # Let's improve by assuming we can look it up via product_id AND warehouse_name
        
        warehouse_name = item['values'][4]
        
        # We need a proper get method in repository that uses name or we should have stored ID.
        # For now, let's use the query inside repository that matches the one in main.py
        
        # NOTE: Repository `get_by_id` assumes we know warehouse_id or it returns one. 
        # But here a product can be in multiple warehouses.
        # Let's adding a helper or just using what we have.
        
        # To fix this cleanly, we should ideally store warehouse_id in the treeview hiddenly.
        # but ttk treeview only stores what is in values.
        
        # Workaround: Fetch by product_id and filter in python or add specific method
        # I'll rely on the existing get_by_id which I modified to take optional warehouse_id 
        # But I don't have warehouse_id here, only name.
        
        # Let's fetch the warehouse ID first? Or just execute a custom query here?
        # Better: Update repository to support lookup by name components if needed, 
        # OR better yet, fix the Treeview to include warehouse_id as a hidden column (not displayed)
        # Detailed implementation of hidden columns is tricky in standard tkinter.
        
        # Simpler approach: Iterate to find match.
        
        # Let's fetch product details using the dedicated method which accepts warehouse_name? 
        # No repository method `get_by_id` takes warehouse_id.
        
        # I will fetch the warehouse_id first using the name.
        
        try:
            # Quick lookup
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT warehouse_id FROM warehouses WHERE warehouse_name = %s", (warehouse_name,))
            res = cur.fetchone()
            conn.close()
            
            if res:
                data = self.repository.get_by_id(prod_id, res['warehouse_id'])
                if data:
                    from dialogs.product_dialog import ProductDialog
                    dialog = ProductDialog(self.root, mode='edit', product_data=dict(data), current_user=self.current_user, db_connection_func=get_db_connection)
                    self.root.wait_window(dialog.dialog)
                    if dialog.result: self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_product(self):
        sel = self.tree.selection()
        if not sel: return
        
        item = self.tree.item(sel[0])
        prod_id = item['values'][0]
        warehouse_name = item['values'][4]
        
        if messagebox.askyesno("Confirm", "Remove product from this warehouse?"):
             # Look up warehouse ID again
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT warehouse_id FROM warehouses WHERE warehouse_name = %s", (warehouse_name,))
            res = cur.fetchone()
            conn.close()
            
            if res:
                self.repository.remove_from_warehouse(prod_id, res['warehouse_id'])
                self.load_data()
