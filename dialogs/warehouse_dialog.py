import tkinter as tk
from tkinter import ttk, messagebox
import pymysql

class WarehouseDialog:
    def __init__(self, parent, mode='add', warehouse_data=None, current_user=None, db_connection_func=None):
        """
        Warehouse Add/Edit Dialog
        
        Args:
            parent: Parent window
            mode: 'add' or 'edit'
            warehouse_data: Dictionary with warehouse data (for edit mode)
            current_user: Current logged-in user dict
            db_connection_func: Function to get DB connection
        """
        self.parent = parent
        self.mode = mode
        self.warehouse_data = warehouse_data or {}
        self.current_user = current_user
        self.get_db_connection = db_connection_func
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Add New' if mode == 'add' else 'Edit'} Warehouse")
        
        # Set dialog size
        dialog_width = 600
        dialog_height = 450
        self.dialog.geometry(f"{dialog_width}x{dialog_height}")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.resizable(True, True)
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
        if mode == 'edit' and warehouse_data:
            self.load_warehouse_data()
    
    def create_ui(self):
        """Create the form UI"""
        # Buttons packed first at bottom to ensure visibility
        btn_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        btn_frame.pack(fill='x', side='bottom', padx=20, pady=20)
        
        tk.Button(btn_frame, text="💾 Save", font=('Segoe UI', 11, 'bold'),
                 bg='#10b981', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.save_warehouse).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Segoe UI', 11),
                 bg='#6b7280', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.dialog.destroy).pack(side='right', padx=5)

        # Container (packed after buttons with expand=True)
        container = tk.Frame(self.dialog, bg='white', bd=0)
        container.pack(fill='both', expand=True, padx=20, pady=(20, 0))
        
        # Header
        header = tk.Frame(container, bg='#0f172a', height=60)
        header.pack(fill='x', pady=(0, 20))
        
        icon = '📦' if self.mode == 'add' else '✏️'
        title = f"{icon} {'Add New Warehouse' if self.mode == 'add' else 'Edit Warehouse'}"
        tk.Label(header, text=title, font=('Segoe UI', 16, 'bold'),
                bg='#0f172a', fg='white').pack(pady=15)
        
        # Scrollable form
        self.canvas = tk.Canvas(container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.canvas.yview)
        scrollable_frame = tk.Frame(self.canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Handle canvas resize
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.canvas.bind('<Configure>', _on_canvas_configure)
        
        # Mousewheel binding
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.dialog.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Form fields
        self.create_form_fields(scrollable_frame)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def create_form_fields(self, parent):
        """Create all form fields"""
        # Name
        self.create_field(parent, "warehouse_name", "Warehouse Name *", tk.Entry)
        
        # Location dropdown
        self.create_dropdown(parent, "location_id", "Location *", self.get_locations())
        
        # Supervisor dropdown
        self.create_dropdown(parent, "supervisor_id", "Supervisor *", self.get_supervisors())
        
        # Capacity
        self.create_field(parent, "capacity", "Capacity (sq ft)", tk.Entry)
    
    def create_field(self, parent, var_name, label, widget_type):
        """Create input field with label and error message"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=10)
        
        # Label
        tk.Label(frame, text=label, font=('Segoe UI', 10),
                bg='white', fg='#475569').pack(anchor='w')
        
        # Widget
        if widget_type == tk.Entry:
            self.vars[var_name] = tk.StringVar()
            widget = tk.Entry(frame, textvariable=self.vars[var_name],
                            font=('Segoe UI', 10), bg='#f8fafc', fg='#1e293b',
                            relief='solid', bd=1)
            widget.pack(fill='x', ipady=7, pady=(3, 0))
        
        # Error label
        error_label = tk.Label(frame, text="", font=('Segoe UI', 9),
                              bg='white', fg='#ef4444')
        error_label.pack(anchor='w')
        self.error_labels[var_name] = error_label
        
        return widget
    
    def create_dropdown(self, parent, var_name, label, options):
        """Create dropdown field"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=10)
        
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
        combo.pack(fill='x', ipady=7, pady=(3, 0))
        
        if display_values:
            combo.current(0)
        
        # Error label
        error_label = tk.Label(frame, text="", font=('Segoe UI', 9),
                              bg='white', fg='#ef4444')
        error_label.pack(anchor='w')
        self.error_labels[var_name] = error_label
        
        return combo
    
    def get_locations(self):
        """Fetch locations from database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT location_id, location_name FROM locations ORDER BY location_name")
            locations = cursor.fetchall()
            conn.close()
            return [(loc['location_name'], loc['location_id']) for loc in locations]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load locations: {e}")
            return []
    
    def get_supervisors(self):
        """Fetch active supervisors from database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.person_id, p.name 
                FROM person p
                JOIN supervisor s ON p.person_id = s.person_id
                WHERE p.is_active = TRUE
                ORDER BY p.name
            """)
            supervisors = cursor.fetchall()
            conn.close()
            return [(sup['name'], sup['person_id']) for sup in supervisors]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load supervisors: {e}")
            return []
    
    def load_warehouse_data(self):
        """Load existing warehouse data into form"""
        data = self.warehouse_data
        
        if 'warehouse_name' in data:
            self.vars['warehouse_name'].set(data['warehouse_name'])
        
        # Location
        if 'location_id' in data and 'location_id_map' in self.vars:
            for display, value in self.vars['location_id_map'].items():
                if value == data['location_id']:
                    self.vars['location_id'].set(display)
                    break
        
        # Supervisor
        if 'supervisor_id' in data and 'supervisor_id_map' in self.vars:
            for display, value in self.vars['supervisor_id_map'].items():
                if value == data['supervisor_id']:
                    self.vars['supervisor_id'].set(display)
                    break
        
        # Capacity
        if 'capacity' in data and data['capacity']:
            self.vars['capacity'].set(str(data['capacity']))
    
    def validate_form(self):
        """Validate form fields"""
        errors = {}
        
        # Required: Warehouse Name
        wh_name = self.vars['warehouse_name'].get().strip()
        if not wh_name:
            errors['warehouse_name'] = "Warehouse name is required"
        elif len(wh_name) < 3:
            errors['warehouse_name'] = "Warehouse name must be at least 3 characters"
        
        # Required: Location
        location = self.vars['location_id'].get().strip()
        if not location:
            errors['location_id'] = "Location is required"
        
        # Required: Supervisor
        supervisor = self.vars['supervisor_id'].get().strip()
        if not supervisor:
            errors['supervisor_id'] = "Supervisor is required"
        
        # Optional: Capacity (must be number if provided)
        capacity_str = self.vars.get('capacity', tk.StringVar()).get().strip()
        if capacity_str:
            try:
                capacity = int(capacity_str)
                if capacity <= 0:
                    errors['capacity'] = "Capacity must be positive"
            except ValueError:
                errors['capacity'] = "Capacity must be a number"
        
        # Display errors
        for field, error_msg in errors.items():
            if field in self.error_labels:
                self.error_labels[field].config(text=f"⚠️ {error_msg}")
        
        # Clear errors for valid fields
        for field in self.error_labels:
            if field not in errors:
                self.error_labels[field].config(text="")
        
        return len(errors) == 0
    
    def save_warehouse(self):
        """Save warehouse to database"""
        if not self.validate_form():
            messagebox.showerror("Validation Error", "Please fix the errors before saving.")
            return
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Extract form data
            wh_name = self.vars['warehouse_name'].get().strip()
            
            loc_display = self.vars['location_id'].get()
            location_id = self.vars['location_id_map'].get(loc_display)
            
            sup_display = self.vars['supervisor_id'].get()
            supervisor_id = self.vars['supervisor_id_map'].get(sup_display)
            
            capacity_str = self.vars.get('capacity', tk.StringVar()).get().strip()
            capacity = int(capacity_str) if capacity_str else None
            
            if self.mode == 'add':
                # Insert new warehouse
                cursor.execute("""
                    INSERT INTO warehouses (warehouse_name, location_id, supervisor_id, capacity)
                    VALUES (%s, %s, %s, %s)
                """, (wh_name, location_id, supervisor_id, capacity))
                
                conn.commit()
                messagebox.showinfo("Success", f"Warehouse '{wh_name}' added successfully!")
            
            else:  # Edit mode
                wh_id = self.warehouse_data['warehouse_id']
                
                # Update warehouse
                cursor.execute("""
                    UPDATE warehouses 
                    SET warehouse_name = %s, location_id = %s, supervisor_id = %s, capacity = %s
                    WHERE warehouse_id = %s
                """, (wh_name, location_id, supervisor_id, capacity, wh_id))
                
                conn.commit()
                messagebox.showinfo("Success", f"Warehouse '{wh_name}' updated successfully!")
            
            conn.close()
            self.result = True
            self.dialog.destroy()
            
        except pymysql.IntegrityError as e:
            messagebox.showerror("Error", f"Database constraint violation: {e}\n\nWarehouse name might already exist.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save warehouse: {e}")
