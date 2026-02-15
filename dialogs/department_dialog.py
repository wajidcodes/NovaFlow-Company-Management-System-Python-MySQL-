import tkinter as tk
from tkinter import ttk, messagebox
import pymysql

class DepartmentDialog:
    def __init__(self, parent, mode='add', department_data=None, db_connection_func=None):
        """
        Department Add/Edit Dialog
        
        Args:
            parent: Parent window
            mode: 'add' or 'edit'
            department_data: Dictionary with department data (for edit mode)
            db_connection_func: Function to get DB connection
        """
        self.parent = parent
        self.mode = mode
        self.department_data = department_data or {}
        self.get_db_connection = db_connection_func
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Add New' if mode == 'add' else 'Edit'} Department")
        
        # Set dialog size
        dialog_width = 500
        dialog_height = 450
        self.dialog.geometry(f"{dialog_width}x{dialog_height}")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.resizable(False, False)
        self.dialog.grab_set()  
        
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
        if mode == 'edit' and department_data:
            self.load_department_data()
    
    def create_ui(self):
        """Create the form UI"""
        # Buttons packed first at bottom to ensure visibility
        btn_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        btn_frame.pack(fill='x', side='bottom', padx=20, pady=20)
        
        tk.Button(btn_frame, text="💾 Save", font=('Segoe UI', 11, 'bold'),
                 bg='#10b981', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.save_department).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Segoe UI', 11),
                 bg='#6b7280', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.dialog.destroy).pack(side='right', padx=5)

        # Container (packed after buttons with expand=True)
        container = tk.Frame(self.dialog, bg='white', bd=0)
        container.pack(fill='both', expand=True, padx=20, pady=(20, 0))
        
        # Header
        header = tk.Frame(container, bg='#0f172a', height=60)
        header.pack(fill='x', pady=(0, 20))
        
        icon = '🏢' if self.mode == 'add' else '✏️'
        title = f"{icon} {'Add New Department' if self.mode == 'add' else 'Edit Department'}"
        tk.Label(header, text=title, font=('Segoe UI', 16, 'bold'),
                bg='#0f172a', fg='white').pack(pady=15)
        
        # Form fields
        form_frame = tk.Frame(container, bg='white')
        form_frame.pack(fill='both', expand=True, pady=10)
        
        # Department Name
        self.create_field(form_frame, "department_name", "Department Name *", tk.Entry)
        
        # Location Dropdown
        self.create_dropdown(form_frame, "location_id", "Location *", self.get_locations())
        
        # HOD Dropdown
        self.create_dropdown(form_frame, "hod_id", "Head of Department", self.get_available_hods())
    
    def create_field(self, parent, var_name, label, widget_type):
        """Create input field with label and error message"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=12)
        
        # Label
        tk.Label(frame, text=label, font=('Segoe UI', 11),
                bg='white', fg='#475569').pack(anchor='w')
        
        # Widget
        if widget_type == tk.Entry:
            self.vars[var_name] = tk.StringVar()
            widget = tk.Entry(frame, textvariable=self.vars[var_name],
                            font=('Segoe UI', 11), bg='#f8fafc', fg='#1e293b',
                            relief='solid', bd=1)
            widget.pack(fill='x', ipady=8, pady=(5, 0))
        
        # Error label
        error_label = tk.Label(frame, text="", font=('Segoe UI', 9),
                              bg='white', fg='#ef4444')
        error_label.pack(anchor='w')
        self.error_labels[var_name] = error_label
        
        return widget
    
    def create_dropdown(self, parent, var_name, label, options):
        """Create dropdown field"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=12)
        
        tk.Label(frame, text=label, font=('Segoe UI', 11),
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
                           values=display_values, font=('Segoe UI', 11),
                           state='readonly')
        combo.pack(fill='x', ipady=8, pady=(5, 0))
        
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
    
    def get_available_hods(self):
        """Fetch available HODs (not already assigned to other departments)"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get HODs not assigned to any department, or assigned to current department (in edit mode)
            if self.mode == 'edit' and 'department_id' in self.department_data:
                cursor.execute("""
                    SELECT p.person_id, p.name 
                    FROM person p
                    JOIN hod h ON p.person_id = h.person_id
                    WHERE p.is_active = TRUE 
                    AND (p.person_id NOT IN (SELECT hod_id FROM departments WHERE hod_id IS NOT NULL)
                         OR p.person_id = %s)
                    ORDER BY p.name
                """, (self.department_data.get('hod_id'),))
            else:
                cursor.execute("""
                    SELECT p.person_id, p.name 
                    FROM person p
                    JOIN hod h ON p.person_id = h.person_id
                    WHERE p.is_active = TRUE 
                    AND p.person_id NOT IN (SELECT hod_id FROM departments WHERE hod_id IS NOT NULL)
                    ORDER BY p.name
                """)
            
            hods = cursor.fetchall()
            conn.close()
            return [("None", None)] + [(hod['name'], hod['person_id']) for hod in hods]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load HODs: {e}")
            return [("None", None)]
    
    def load_department_data(self):
        """Load existing department data into form"""
        data = self.department_data
        
        if 'department_name' in data:
            self.vars['department_name'].set(data['department_name'])
        
        # Location
        if 'location_id' in data and 'location_id_map' in self.vars:
            for display, value in self.vars['location_id_map'].items():
                if value == data['location_id']:
                    self.vars['location_id'].set(display)
                    break
        
        # HOD
        if 'hod_id' in data and data['hod_id'] and 'hod_id_map' in self.vars:
            for display, value in self.vars['hod_id_map'].items():
                if value == data['hod_id']:
                    self.vars['hod_id'].set(display)
                    break
    
    def validate_form(self):
        """Validate form fields"""
        errors = {}
        
        # Required: Department Name
        dept_name = self.vars['department_name'].get().strip()
        if not dept_name:
            errors['department_name'] = "Department name is required"
        elif len(dept_name) < 3:
            errors['department_name'] = "Department name must be at least 3 characters"
        
        # Required: Location
        location = self.vars['location_id'].get().strip()
        if not location:
            errors['location_id'] = "Location is required"
        
        # Display errors
        for field, error_msg in errors.items():
            if field in self.error_labels:
                self.error_labels[field].config(text=f"⚠️ {error_msg}")
        
        # Clear errors for valid fields
        for field in self.error_labels:
            if field not in errors:
                self.error_labels[field].config(text="")
        
        return len(errors) == 0
    
    def save_department(self):
        """Save department to database"""
        if not self.validate_form():
            messagebox.showerror("Validation Error", "Please fix the errors before saving.")
            return
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Extract form data
            dept_name = self.vars['department_name'].get().strip()
            
            location_display = self.vars['location_id'].get()
            location_id = self.vars['location_id_map'].get(location_display)
            
            hod_display = self.vars['hod_id'].get()
            hod_id = self.vars.get('hod_id_map', {}).get(hod_display)
            
            if self.mode == 'add':
                # Insert new department
                cursor.execute("""
                    INSERT INTO departments (department_name, location_id, hod_id)
                    VALUES (%s, %s, %s)
                """, (dept_name, location_id, hod_id))
                
                conn.commit()
                messagebox.showinfo("Success", f"Department '{dept_name}' added successfully!")
            
            else:  # Edit mode
                dept_id = self.department_data['department_id']
                
                # Update department
                cursor.execute("""
                    UPDATE departments 
                    SET department_name = %s, location_id = %s, hod_id = %s
                    WHERE department_id = %s
                """, (dept_name, location_id, hod_id, dept_id))
                
                conn.commit()
                messagebox.showinfo("Success", f"Department '{dept_name}' updated successfully!")
            
            conn.close()
            self.result = True
            self.dialog.destroy()
            
        except pymysql.IntegrityError as e:
            messagebox.showerror("Error", f"Database constraint violation: {e}\n\nDepartment name might already exist.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save department: {e}")
