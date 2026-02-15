"""
Warehouse View - Manages warehouse UI interactions
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView
from models.warehouse_repository import WarehouseRepository
from config.database import get_db_connection

class WarehouseView(BaseView):
    def create_ui(self):
        self.repository = WarehouseRepository()
        self.search_var = tk.StringVar()

        self.create_header("📦 Warehouse Management", "#7c3aed")
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

        # Actions
        btn_frame = tk.Frame(toolbar, bg='white')
        btn_frame.pack(side='right')
        
        if self.current_user['person_type'] == 'HOD':
            self.create_button(btn_frame, "➕ Add", self.add_warehouse, "#10b981")
            self.create_button(btn_frame, "✏️ Edit", self.edit_warehouse, "#3b82f6")
            self.create_button(btn_frame, "🗑️ Delete", self.delete_warehouse, "#ef4444")
            
        self.create_button(btn_frame, "🔄 Refresh", self.load_data, "#6b7280")

    def create_treeview(self):
        columns = ('ID', 'Warehouse Name', 'Location', 'Supervisor', 'Capacity', 'Products')
        self.tree = super().create_treeview(columns)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Warehouse Name', text='Warehouse Name')
        self.tree.heading('Location', text='Location')
        self.tree.heading('Supervisor', text='Supervisor')
        self.tree.heading('Capacity', text='Capacity')
        self.tree.heading('Products', text='Products Count')
        
        self.tree.column('ID', width=50, anchor='center')
        
        self.tree.tag_configure('oddrow', background='#f8fafc')
        self.tree.tag_configure('evenrow', background='white')
        
        self.tree.bind('<Double-1>', lambda e: self.edit_warehouse())

    def load_data(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            sup_id = self.current_user['person_id'] if self.current_user['person_type'] == 'SUPERVISOR' else None
            
            warehouses = self.repository.get_all(
                supervisor_id=sup_id,
                search_term=self.search_var.get()
            )
            
            for idx, wh in enumerate(warehouses):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                self.tree.insert('', 'end', values=(
                    wh['warehouse_id'], wh['warehouse_name'], wh['location_name'] or 'N/A',
                    wh['supervisor_name'] or 'Unassigned', wh['capacity'] or '-', wh['product_count']
                ), tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_warehouse(self):
        from dialogs.warehouse_dialog import WarehouseDialog
        dialog = WarehouseDialog(self.root, mode='add', current_user=self.current_user, db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        if dialog.result: self.load_data()

    def edit_warehouse(self):
        sel = self.tree.selection()
        if not sel: return
        
        wh_id = self.tree.item(sel[0])['values'][0]
        data = self.repository.get_by_id(wh_id)
        
        from dialogs.warehouse_dialog import WarehouseDialog
        dialog = WarehouseDialog(self.root, mode='edit', warehouse_data=dict(data), current_user=self.current_user, db_connection_func=get_db_connection)
        self.root.wait_window(dialog.dialog)
        if dialog.result: self.load_data()

    def delete_warehouse(self):
        sel = self.tree.selection()
        if not sel: return
        
        item = self.tree.item(sel[0])
        wh_id = item['values'][0]
        prod_count = item['values'][5]
        
        if prod_count > 0:
            messagebox.showerror("Cannot Delete", "Cannot delete warehouse with products.")
            return

        if messagebox.askyesno("Confirm", "Delete warehouse?"):
            self.repository.delete(wh_id)
            self.load_data()
