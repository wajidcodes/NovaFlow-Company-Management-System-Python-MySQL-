import tkinter as tk
from tkinter import ttk, messagebox
import pymysql

class ProductDialog:
    def __init__(self, parent, mode='add', product_data=None, current_user=None, db_connection_func=None):
        """
        Product Add/Edit Dialog
        
        Args:
            parent: Parent window
            mode: 'add' or 'edit'
            product_data: Dictionary with product data (for edit mode)
            current_user: Current logged-in user dict
            db_connection_func: Function to get DB connection
        """
        self.parent = parent
        self.mode = mode
        self.product_data = product_data or {}
        self.current_user = current_user
        self.get_db_connection = db_connection_func
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Add New' if mode == 'add' else 'Edit'} Product")
        
        # Set dialog size
        dialog_width = 550
        # Set dialog size
        dialog_width = 650
        dialog_height = 650
        self.dialog.geometry(f"{dialog_width}x{dialog_height}")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.resizable(False, False)
        self.dialog.grab_set()  # Make modal
        
        # Center the window on screen
        self.dialog.update_idletasks()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2) - 30
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Variables
        self.vars = {}
        self.error_labels = {}
        
        self.create_ui()
        
        # Pre-fill data in edit mode
        if mode == 'edit' and product_data:
            self.load_product_data()
    
    def create_ui(self):
        """Create the form UI"""
        # Container
        container = tk.Frame(self.dialog, bg='white', bd=0)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Frame(container, bg='#0f172a', height=60)
        header.pack(fill='x', pady=(0, 20))
        
        icon = '📦' if self.mode == 'add' else '✏️'
        title = f"{icon} {'Add New Product' if self.mode == 'add' else 'Edit Product'}"
        tk.Label(header, text=title, font=('Segoe UI', 16, 'bold'),
                bg='#0f172a', fg='white').pack(pady=15)
        
        # Scrollable Form Container
        canvas_container = tk.Frame(container, bg='white')
        canvas_container.pack(fill='both', expand=True)
        
        # Canvas and Scrollbar
        self.canvas = tk.Canvas(canvas_container, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=580) # Adjust width as needed
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind MouseWheel
        self.dialog.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Use scrollable_frame instead of local form_frame
        form_frame = self.scrollable_frame
        
        # Product Name
        self.create_field(form_frame, "product_name", "Product Name *", tk.Entry)
        
        # Product Type
        self.create_field(form_frame, "product_type", "Product Type/Category", tk.Entry)
        
        # Unit Price
        self.create_field(form_frame, "unit_price", "Unit Price ($) *", tk.Entry)
        
        # Warehouse dropdown
        self.create_dropdown(form_frame, "warehouse_id", "Warehouse *", self.get_user_warehouses())
        
        # Stock Quantity
        self.create_field(form_frame, "stock_quantity", "Stock Quantity", tk.Entry)
        
        # Description (Text widget)
        desc_frame = tk.Frame(form_frame, bg='white')
        desc_frame.pack(fill='x', pady=8)
        
        tk.Label(desc_frame, text="Description", font=('Segoe UI', 10),
                bg='white', fg='#475569').pack(anchor='w')
        
        self.desc_text = tk.Text(desc_frame, font=('Segoe UI', 10), bg='#f8fafc',
                                fg='#1e293b', relief='solid', bd=1, height=3, wrap='word')
        self.desc_text.pack(fill='x', pady=(3, 0))
        
        # Buttons
        btn_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        btn_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        tk.Button(btn_frame, text="💾 Save", font=('Segoe UI', 11, 'bold'),
                 bg='#10b981', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.save_product).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Segoe UI', 11),
                 bg='#6b7280', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.dialog.destroy).pack(side='right', padx=5)
    
    def create_field(self, parent, var_name, label, widget_type):
        """Create input field with label and error message"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=8)
        
        # Label
        tk.Label(frame, text=label, font=('Segoe UI', 10),
                bg='white', fg='#475569').pack(anchor='w')
        
        # Widget
        if widget_type == tk.Entry:
            self.vars[var_name] = tk.StringVar()
            widget = tk.Entry(frame, textvariable=self.vars[var_name],
                            font=('Segoe UI', 10), bg='#f8fafc', fg='#1e293b',
                            relief='solid', bd=1)
            widget.pack(fill='x', ipady=6, pady=(3, 0))
        
        # Error label
        error_label = tk.Label(frame, text="", font=('Segoe UI', 9),
                              bg='white', fg='#ef4444')
        error_label.pack(anchor='w')
        self.error_labels[var_name] = error_label
        
        return widget
    
    def create_dropdown(self, parent, var_name, label, options):
        """Create dropdown field"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=8)
        
        tk.Label(frame, text=label, font=('Segoe UI', 10),
                bg='white', fg='#475569').pack(anchor='w')
        
        self.vars[var_name] = tk.StringVar()
        
        # Prepare display values and mapping
        if options and isinstance(options[0], tuple):
            display_values = [opt[0] for opt in options]
            self.vars[f"{var_name}_map"] = {opt[0]: opt[1] for opt in options}
            self.vars[f"{var_name}_reverse_map"] = {opt[1]: opt[0] for opt in options}
        else:
            display_values = options
        
        combo = ttk.Combobox(frame, textvariable=self.vars[var_name],
                           values=display_values, font=('Segoe UI', 10),
                           state='readonly')
        combo.pack(fill='x', ipady=6, pady=(3, 0))
        
        if display_values:
            combo.current(0)
        
        # Error label
        error_label = tk.Label(frame, text="", font=('Segoe UI', 9),
                              bg='white', fg='#ef4444')
        error_label.pack(anchor='w')
        self.error_labels[var_name] = error_label
        
        return combo
    
    def get_user_warehouses(self):
        """Fetch warehouses based on user role"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            role = self.current_user['person_type']
            user_id = self.current_user['person_id']
            
            if role == 'SUPERVISOR':
                # Supervisors see only their assigned warehouses
                cursor.execute("""
                    SELECT warehouse_id, warehouse_name 
                    FROM warehouses 
                    WHERE supervisor_id = %s
                    ORDER BY warehouse_name
                """, (user_id,))
            else:
                # HOD and others see all warehouses
                cursor.execute("""
                    SELECT warehouse_id, warehouse_name 
                    FROM warehouses 
                    ORDER BY warehouse_name
                """)
            
            warehouses = cursor.fetchall()
            conn.close()
            
            if not warehouses:
                return [("No warehouses available", None)]
            
            return [(wh['warehouse_name'], wh['warehouse_id']) for wh in warehouses]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load warehouses: {e}")
            return [("Error loading warehouses", None)]
    
    def load_product_data(self):
        """Load existing product data into form"""
        data = self.product_data
        
        if 'product_name' in data:
            self.vars['product_name'].set(data['product_name'])
        
        if 'product_type' in data and data['product_type']:
            self.vars['product_type'].set(data['product_type'])
        
        if 'unit_price' in data:
            self.vars['unit_price'].set(str(data['unit_price']))
        
        if 'stock_quantity' in data and data['stock_quantity'] is not None:
            self.vars['stock_quantity'].set(str(data['stock_quantity']))
        
        # Warehouse
        if 'warehouse_id' in data and 'warehouse_id_map' in self.vars:
            for display, value in self.vars['warehouse_id_map'].items():
                if value == data['warehouse_id']:
                    self.vars['warehouse_id'].set(display)
                    break
        
        # Description
        if 'description' in data and data['description']:
            self.desc_text.insert('1.0', data['description'])
    
    def validate_form(self):
        """Validate form fields"""
        errors = {}
        
        # Required: Product Name
        product_name = self.vars['product_name'].get().strip()
        if not product_name:
            errors['product_name'] = "Product name is required"
        elif len(product_name) < 2:
            errors['product_name'] = "Product name must be at least 2 characters"
        
        # Required: Unit Price
        price_str = self.vars['unit_price'].get().strip()
        if not price_str:
            errors['unit_price'] = "Unit price is required"
        else:
            try:
                price = float(price_str)
                if price < 0:
                    errors['unit_price'] = "Price must be non-negative"
            except ValueError:
                errors['unit_price'] = "Price must be a valid number"
        
        # Required: Warehouse
        warehouse = self.vars['warehouse_id'].get().strip()
        if not warehouse or warehouse == "No warehouses available":
            errors['warehouse_id'] = "Warehouse is required"
        
        # Optional: Stock Quantity (must be number if provided)
        stock_str = self.vars.get('stock_quantity', tk.StringVar()).get().strip()
        if stock_str:
            try:
                stock = int(stock_str)
                if stock < 0:
                    errors['stock_quantity'] = "Stock quantity must be non-negative"
            except ValueError:
                errors['stock_quantity'] = "Stock quantity must be a whole number"
        
        # Display errors
        for field, error_msg in errors.items():
            if field in self.error_labels:
                self.error_labels[field].config(text=f"⚠️ {error_msg}")
        
        # Clear errors for valid fields
        for field in self.error_labels:
            if field not in errors:
                self.error_labels[field].config(text="")
        
        return len(errors) == 0
    
    def save_product(self):
        """Save product to database (Normalized Schema)"""
        if not self.validate_form():
            messagebox.showerror("Validation Error", "Please fix the errors before saving.")
            return
        
        conn = None
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Extract form data
            product_name = self.vars['product_name'].get().strip()
            product_type = self.vars.get('product_type', tk.StringVar()).get().strip() or None
            unit_price = float(self.vars['unit_price'].get().strip())
            
            wh_display = self.vars['warehouse_id'].get()
            warehouse_id = self.vars['warehouse_id_map'].get(wh_display)
            
            stock_str = self.vars.get('stock_quantity', tk.StringVar()).get().strip()
            stock_quantity = int(stock_str) if stock_str else 0
            
            description = self.desc_text.get('1.0', 'end-1c').strip() or None
            
            # Check if product exists (Global Catalog)
            cursor.execute("SELECT product_id FROM products WHERE product_name = %s", (product_name,))
            existing_prod = cursor.fetchone()
            
            product_id = None
            
            if existing_prod:
                product_id = existing_prod['product_id']
                # Update catalog details if changed (optional, but good for edits)
                cursor.execute("""
                    UPDATE products 
                    SET product_type = %s, unit_price = %s, description = %s
                    WHERE product_id = %s
                """, (product_type, unit_price, description, product_id))
            else:
                # Insert new product into catalog
                cursor.execute("""
                    INSERT INTO products (product_name, product_type, unit_price, description)
                    VALUES (%s, %s, %s, %s)
                """, (product_name, product_type, unit_price, description))
                product_id = cursor.lastrowid
            
            # Now handle Warehouse Stock (warehouse_products)
            
            # Check if link exists
            cursor.execute("""
                SELECT warehouse_product_id FROM warehouse_products 
                WHERE warehouse_id = %s AND product_id = %s
            """, (warehouse_id, product_id))
            link = cursor.fetchone()
            
            if link:
                # Update existing stock
                cursor.execute("""
                    UPDATE warehouse_products 
                    SET qty = %s
                    WHERE warehouse_product_id = %s
                """, (stock_quantity, link['warehouse_product_id']))
                
                # If switching warehouses in edit mode, we might need to handle the old warehouse entry.
                # But typically 'edit' here means editing THIS specific warehouse-product entry.
                # If user changes warehouse in dropdown during edit, it effectively moves stock or updates another entry.
                # For simplicity, we just update the entry for the selected warehouse.
            else:
                # Insert new stock entry
                cursor.execute("""
                    INSERT INTO warehouse_products (warehouse_id, product_id, qty)
                    VALUES (%s, %s, %s)
                """, (warehouse_id, product_id, stock_quantity))
            
            conn.commit()
            
            if self.mode == 'add':
                messagebox.showinfo("Success", f"Product '{product_name}' linked to warehouse successfully!")
            else:
                messagebox.showinfo("Success", "Product details updated successfully!")
            
            conn.close()
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            messagebox.showerror("Error", f"Failed to save product: {e}")

    def _on_mousewheel(self, event):
        if self.canvas:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
