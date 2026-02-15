import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
from services.auth_service import AuthService
import re
from datetime import datetime

class EmployeeDialog:
    def __init__(self, parent, mode='add', employee_data=None, current_user=None, db_connection_func=None):
        """
        Employee Add/Edit Dialog
        
        Args:
            parent: Parent window
            mode: 'add' or 'edit'
            employee_data: Dictionary with employee data (for edit mode)
            current_user: Current logged-in user dict
            db_connection_func: Function to get DB connection
        """
        self.parent = parent
        self.mode = mode
        self.employee_data = employee_data or {}
        self.current_user = current_user
        self.get_db_connection = db_connection_func
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Add New' if mode == 'add' else 'Edit'} Employee")
        
        # Set reasonable dialog size
        dialog_width = 800
        dialog_height = 600
        self.dialog.geometry(f"{dialog_width}x{dialog_height}")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.resizable(True, True)
        self.dialog.grab_set()  # Make modal
        
        # Center the window on screen
        self.dialog.update_idletasks()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2) - 30  # Slightly higher
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Variables
        self.vars = {}
        self.error_labels = {}
        
        self.create_ui()
        
        # Pre-fill data in edit mode
        if mode == 'edit' and employee_data:
            self.load_employee_data()
    
    def create_ui(self):
        """Create the form UI"""
        # Buttons packed first at bottom to ensure visibility
        btn_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        btn_frame.pack(fill='x', side='bottom', padx=20, pady=20)
        
        tk.Button(btn_frame, text="💾 Save", font=('Segoe UI', 11, 'bold'),
                 bg='#10b981', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.save_employee).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Segoe UI', 11),
                 bg='#6b7280', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.dialog.destroy).pack(side='right', padx=5)

        # Container (packed after buttons with expand=True)
        container = tk.Frame(self.dialog, bg='white', bd=0)
        container.pack(fill='both', expand=True, padx=20, pady=(20, 0))
        
        # Header
        header = tk.Frame(container, bg='#0f172a', height=60)
        header.pack(fill='x', pady=(0, 20))
        
        icon = '👤' if self.mode == 'add' else '✏️'
        title = f"{icon} {'Add New Employee' if self.mode == 'add' else 'Edit Employee'}"
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
        # Basic Information Section
        self.create_section_header(parent, "📝 Basic Information")
        
        self.create_field(parent, "name", "Full Name *", tk.Entry)
        self.create_field(parent, "email", "Email Address *", tk.Entry)
        self.create_field(parent, "phone", "Phone Number * (11 digits)", tk.Entry)
        self.create_field(parent, "national_insurance", "National Insurance Number *", tk.Entry)
        self.create_field(parent, "date_of_birth", "Date of Birth (YYYY-MM-DD)", tk.Entry)
        self.create_field(parent, "address", "Address", tk.Text, height=3)
        
        # Employment Details Section
        self.create_section_header(parent, "💼 Employment Details")
        
        # Department dropdown
        self.create_dropdown(parent, "department_id", "Department *", self.get_departments())
        
        # Person Type dropdown
        person_types = [
            ('General Employee', 'GENERAL_EMPLOYEE'),
            ('Supervisor', 'SUPERVISOR'),
            ('Salesman', 'SALESMAN'),
            ('HOD', 'HOD')
        ]
        self.create_dropdown(parent, "person_type", "Employee Type *", person_types)
        
        # Track person_type changes to show/hide salary fields
        self.vars['person_type'].trace('w', lambda *args: self.update_salary_fields())
        
        # Supervisor dropdown (for non-supervisors/HOD)
        self.create_dropdown(parent, "supervisor_id", "Supervisor", self.get_supervisors())
        
        self.create_field(parent, "start_date", "Start Date (YYYY-MM-DD)", tk.Entry)
        
        # Salary Section (Dynamic based on person_type)
        self.salary_frame = tk.Frame(parent, bg='white')
        self.salary_frame.pack(fill='x', pady=10)
        
        self.create_section_header(self.salary_frame, "💰 Compensation")
        
        # These will be shown/hidden based on person_type
        self.fixed_salary_widget = self.create_field(self.salary_frame, "fixed_salary", "Fixed Salary (PKR) *", tk.Entry)
        self.hourly_rate_widget = self.create_field(self.salary_frame, "hourly_rate", "Hourly Rate (PKR) *", tk.Entry)
        self.commission_widget = self.create_field(self.salary_frame, "commission_rate", "Commission Rate (%) *", tk.Entry)
        
        # Initial state
        self.update_salary_fields()
        
        # Status checkbox
        status_frame = tk.Frame(parent, bg='white')
        status_frame.pack(fill='x', pady=10)
        
        self.vars['is_active'] = tk.BooleanVar(value=True)
        tk.Checkbutton(status_frame, text="✅ Active Employee", variable=self.vars['is_active'],
                      font=('Segoe UI', 10), bg='white', fg='#1e293b',
                      selectcolor='white').pack(anchor='w')
    
    def create_section_header(self, parent, text):
        """Create section header"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='x', pady=(15, 10))
        
        tk.Label(frame, text=text, font=('Segoe UI', 12, 'bold'),
                bg='white', fg='#1e293b').pack(anchor='w')
        
        tk.Frame(frame, bg='#cbd5e1', height=2).pack(fill='x', pady=(5, 0))
    
    def create_field(self, parent, var_name, label, widget_type, **kwargs):
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
        elif widget_type == tk.Text:
            height = kwargs.get('height', 3)
            widget = tk.Text(frame, font=('Segoe UI', 10), bg='#f8fafc',
                           fg='#1e293b', relief='solid', bd=1, height=height)
            widget.pack(fill='x', pady=(3, 0))
            self.vars[var_name] = widget  # Store widget reference for Text
        
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
    
    def update_salary_fields(self):
        """Show/hide salary fields based on person_type"""
        person_type_display = self.vars['person_type'].get()
        
        # Get actual value from mapping
        if 'person_type_map' in self.vars and person_type_display in self.vars['person_type_map']:
            person_type = self.vars['person_type_map'][person_type_display]
        else:
            person_type = person_type_display
        
        # Hide all salary fields first
        for widget in [self.fixed_salary_widget, self.hourly_rate_widget, self.commission_widget]:
            widget.master.pack_forget()
        
        # Show relevant fields
        if person_type in ['HOD', 'SUPERVISOR']:
            self.fixed_salary_widget.master.pack(fill='x', pady=8)
        elif person_type == 'SALESMAN':
            self.hourly_rate_widget.master.pack(fill='x', pady=8)
            self.commission_widget.master.pack(fill='x', pady=8)
        elif person_type == 'GENERAL_EMPLOYEE':
            self.hourly_rate_widget.master.pack(fill='x', pady=8)
        
        # Update supervisor dropdown visibility
        supervisor_visible = person_type not in ['HOD', 'SUPERVISOR']
        # Note: supervisor dropdown management would go here
    
    def get_departments(self):
        """Fetch departments from database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
            depts = cursor.fetchall()
            conn.close()
            return [(d['department_name'], d['department_id']) for d in depts]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load departments: {e}")
            return []
    
    def get_supervisors(self):
        """Fetch supervisors from database"""
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
            return [("None", None)] + [(s['name'], s['person_id']) for s in supervisors]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load supervisors: {e}")
            return [("None", None)]
    
    def load_employee_data(self):
        """Load existing employee data into form"""
        data = self.employee_data
        
        # Basic fields
        if 'name' in data:
            self.vars['name'].set(data['name'])
        if 'email' in data:
            self.vars['email'].set(data['email'])
        if 'phone' in data:
            self.vars['phone'].set(data['phone'])
        if 'national_insurance' in data:
            self.vars['national_insurance'].set(data['national_insurance'])
        if 'date_of_birth' in data and data['date_of_birth']:
            self.vars['date_of_birth'].set(str(data['date_of_birth']))
        if 'address' in data and data['address']:
            self.vars['address'].insert('1.0', data['address'])
        if 'start_date' in data and data['start_date']:
            self.vars['start_date'].set(str(data['start_date']))
        
        # Department
        if 'department_id' in data and 'department_name_reverse_map' in self.vars:
            for display, value in self.vars['department_id_map'].items():
                if value == data['department_id']:
                    self.vars['department_id'].set(display)
                    break
        
        # Person Type
        if 'person_type' in data and 'person_type_reverse_map' in self.vars:
            display = self.vars['person_type_reverse_map'].get(data['person_type'])
            if display:
                self.vars['person_type'].set(display)
        
        # Salary fields
        if 'fixed_salary' in data:
            self.vars['fixed_salary'].set(str(data['fixed_salary']))
        if 'hourly_rate' in data:
            self.vars['hourly_rate'].set(str(data['hourly_rate']))
        if 'commission_rate' in data:
            self.vars['commission_rate'].set(str(data['commission_rate']))
        
        # Status
        if 'is_active' in data:
            self.vars['is_active'].set(bool(data['is_active']))
            
        # Supervisor
        if 'supervisor_id' in data and data['supervisor_id'] and 'supervisor_id_reverse_map' in self.vars:
            display = self.vars['supervisor_id_reverse_map'].get(data['supervisor_id'])
            if display:
                self.vars['supervisor_id'].set(display)
    
    def validate_form(self):
        """Validate all form fields"""
        errors = {}
        
        # Required fields
        required = ['name', 'email', 'phone', 'national_insurance', 'department_id', 'person_type']
        
        for field in required:
            value = self.vars[field].get().strip() if isinstance(self.vars[field], tk.StringVar) else ""
            if not value:
                errors[field] = "This field is required"
        
        # Email validation
        email = self.vars['email'].get().strip()
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = "Invalid email format"
        
        # Phone validation (11 digits)
        phone = self.vars['phone'].get().strip()
        if phone and not re.match(r'^\d{11}$', phone):
            errors['phone'] = "Phone must be exactly 11 digits"
        
        # Date validation
        for date_field in ['date_of_birth', 'start_date']:
            date_str = self.vars.get(date_field, tk.StringVar()).get().strip()
            if date_str:
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    errors[date_field] = "Invalid date format (use YYYY-MM-DD)"
        
        # Salary validation based on person_type
        person_type_display = self.vars['person_type'].get()
        person_type = self.vars.get('person_type_map', {}).get(person_type_display, person_type_display)
        
        if person_type in ['HOD', 'SUPERVISOR']:
            if not self.vars.get('fixed_salary', tk.StringVar()).get().strip():
                errors['fixed_salary'] = "Fixed salary is required"
            else:
                try:
                    float(self.vars['fixed_salary'].get())
                except ValueError:
                    errors['fixed_salary'] = "Must be a valid number"
        
        elif person_type == 'SALESMAN':
            if not self.vars.get('hourly_rate', tk.StringVar()).get().strip():
                errors['hourly_rate'] = "Hourly rate is required"
            if not self.vars.get('commission_rate', tk.StringVar()).get().strip():
                errors['commission_rate'] = "Commission rate is required"
        
        elif person_type == 'GENERAL_EMPLOYEE':
            if not self.vars.get('hourly_rate', tk.StringVar()).get().strip():
                errors['hourly_rate'] = "Hourly rate is required"
        
        # Display errors
        for field, error_msg in errors.items():
            if field in self.error_labels:
                self.error_labels[field].config(text=f"⚠️ {error_msg}")
        
        # Clear errors for valid fields
        for field in self.error_labels:
            if field not in errors:
                self.error_labels[field].config(text="")
        
        return len(errors) == 0
    
    def save_employee(self):
        """Save employee to database"""
        if not self.validate_form():
            messagebox.showerror("Validation Error", "Please fix the errors before saving.")
            return
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Extract form data
            person_type_display = self.vars['person_type'].get()
            person_type = self.vars['person_type_map'].get(person_type_display, person_type_display)
            
            dept_display = self.vars['department_id'].get()
            department_id = self.vars['department_id_map'].get(dept_display)
            
            # Get address from Text widget
            address = self.vars['address'].get('1.0', 'end-1c').strip() if hasattr(self.vars['address'], 'get') else ""
            
            # Prepare data
            person_data = {
                'name': self.vars['name'].get().strip(),
                'email': self.vars['email'].get().strip(),
                'phone': self.vars['phone'].get().strip(),
                'national_insurance': self.vars['national_insurance'].get().strip(),
                'date_of_birth': self.vars.get('date_of_birth', tk.StringVar()).get().strip() or None,
                'address': address or None,
                'start_date': self.vars.get('start_date', tk.StringVar()).get().strip() or None,
                'department_id': department_id,
                'person_type': person_type,
                'is_active': self.vars['is_active'].get()
            }
            
            if self.mode == 'add':
                # Generate default password (should be changed on first login)
                password_hash = AuthService.hash_password('password123')
                
                # Insert into person table
                cursor.execute("""
                    INSERT INTO person (
                        name, email, phone, national_insurance, date_of_birth,
                        address, start_date, department_id, person_type,
                        password_hash, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    person_data['name'], person_data['email'], person_data['phone'],
                    person_data['national_insurance'], person_data['date_of_birth'],
                    person_data['address'], person_data['start_date'],
                    person_data['department_id'], person_data['person_type'],
                    password_hash, person_data['is_active']
                ))
                
                person_id = cursor.lastrowid
                
                # Insert into specialization table
                if person_type in ['HOD', 'SUPERVISOR']:
                    fixed_salary = float(self.vars['fixed_salary'].get())
                    table = 'hod' if person_type == 'HOD' else 'supervisor'
                    cursor.execute(f"INSERT INTO {table} (person_id, fixed_salary) VALUES (%s, %s)",
                                 (person_id, fixed_salary))
                
                elif person_type == 'SALESMAN':
                    hourly_rate = float(self.vars['hourly_rate'].get())
                    commission_rate = float(self.vars['commission_rate'].get())
                    cursor.execute(
                        "INSERT INTO salesman (person_id, hourly_rate, commission_rate) VALUES (%s, %s, %s)",
                        (person_id, hourly_rate, commission_rate)
                    )
                
                elif person_type == 'GENERAL_EMPLOYEE':
                    hourly_rate = float(self.vars['hourly_rate'].get())
                    cursor.execute(
                        "INSERT INTO general_employee (person_id, hourly_rate) VALUES (%s, %s)",
                        (person_id, hourly_rate)
                    )
                
                # Assign supervisor if applicable
                if person_type not in ['HOD', 'SUPERVISOR']:
                    supervisor_display = self.vars.get('supervisor_id', tk.StringVar()).get()
                    if supervisor_display and 'supervisor_id_map' in self.vars:
                        supervisor_id = self.vars['supervisor_id_map'].get(supervisor_display)
                        if supervisor_id:
                            cursor.execute(
                                "INSERT INTO emp_supervisor (employee_id, supervisor_id) VALUES (%s, %s)",
                                (person_id, supervisor_id)
                            )
                
                conn.commit()
                messagebox.showinfo("Success", f"Employee '{person_data['name']}' added successfully!")
            
            else:  # Edit mode
                person_id = self.employee_data['person_id']
                
                # Update person table
                cursor.execute("""
                    UPDATE person SET
                        name=%s, email=%s, phone=%s, national_insurance=%s,
                        date_of_birth=%s, address=%s, start_date=%s,
                        department_id=%s, is_active=%s
                    WHERE person_id=%s
                """, (
                    person_data['name'], person_data['email'], person_data['phone'],
                    person_data['national_insurance'], person_data['date_of_birth'],
                    person_data['address'], person_data['start_date'],
                    person_data['department_id'], person_data['is_active'],
                    person_id
                ))
                
                # Update specialization table
                if person_type in ['HOD', 'SUPERVISOR']:
                    fixed_salary = float(self.vars['fixed_salary'].get())
                    table = 'hod' if person_type == 'HOD' else 'supervisor'
                    cursor.execute(f"UPDATE {table} SET fixed_salary=%s WHERE person_id=%s",
                                 (fixed_salary, person_id))
                
                elif person_type == 'SALESMAN':
                    hourly_rate = float(self.vars['hourly_rate'].get())
                    commission_rate = float(self.vars['commission_rate'].get())
                    cursor.execute(
                        "UPDATE salesman SET hourly_rate=%s, commission_rate=%s WHERE person_id=%s",
                        (hourly_rate, commission_rate, person_id)
                    )
                
                elif person_type == 'GENERAL_EMPLOYEE':
                    hourly_rate = float(self.vars['hourly_rate'].get())
                    cursor.execute(
                        "UPDATE general_employee SET hourly_rate=%s WHERE person_id=%s",
                        (hourly_rate, person_id)
                    )
                
                # Update Supervisor Logic (Handle Insert/Update/Delete)
                if person_type not in ['HOD', 'SUPERVISOR']:
                    supervisor_display = self.vars.get('supervisor_id', tk.StringVar()).get()
                    supervisor_id = None
                    if supervisor_display and 'supervisor_id_map' in self.vars:
                        supervisor_id = self.vars['supervisor_id_map'].get(supervisor_display)
                    
                    # Delete existing relationship
                    cursor.execute("DELETE FROM emp_supervisor WHERE employee_id = %s", (person_id,))
                    
                    # Insert new if selected
                    if supervisor_id:
                         cursor.execute(
                            "INSERT INTO emp_supervisor (employee_id, supervisor_id) VALUES (%s, %s)",
                            (person_id, supervisor_id)
                        )

                conn.commit()
                messagebox.showinfo("Success", f"Employee '{person_data['name']}' updated successfully!")
            
            conn.close()
            self.result = True
            self.dialog.destroy()
            
        except pymysql.IntegrityError as e:
            messagebox.showerror("Error", f"Database constraint violation: {e}\n\nEmail, Phone, or NI number might already exist.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save employee: {e}")
