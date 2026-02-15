import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
from datetime import datetime

class ProjectDialog:
    def __init__(self, parent, mode='add', project_data=None, current_user=None, db_connection_func=None):
        """
        Project Add/Edit Dialog
        
        Args:
            parent: Parent window
            mode: 'add' or 'edit'
            project_data: Dictionary with project data (for edit mode)
            current_user: Current logged-in user dict
            db_connection_func: Function to get DB connection
        """
        self.parent = parent
        self.mode = mode
        self.project_data = project_data or {}
        self.current_user = current_user
        self.get_db_connection = db_connection_func
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Add New' if mode == 'add' else 'Edit'} Project")
        
        # Set dialog size
        dialog_width = 650
        dialog_height = 550
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
        if mode == 'edit' and project_data:
            self.load_project_data()
    
    def create_ui(self):
        """Create the form UI"""
        # Buttons packed first at bottom to ensure visibility
        btn_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        btn_frame.pack(fill='x', side='bottom', padx=20, pady=20)
        
        tk.Button(btn_frame, text="💾 Save", font=('Segoe UI', 11, 'bold'),
                 bg='#10b981', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.save_project).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Segoe UI', 11),
                 bg='#6b7280', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.dialog.destroy).pack(side='right', padx=5)

        # Container (packed after buttons with expand=True)
        container = tk.Frame(self.dialog, bg='white', bd=0)
        container.pack(fill='both', expand=True, padx=20, pady=(20, 0))
        
        # Header
        header = tk.Frame(container, bg='#0f172a', height=60)
        header.pack(fill='x', pady=(0, 20))
        
        icon = '📋' if self.mode == 'add' else '✏️'
        title = f"{icon} {'Add New Project' if self.mode == 'add' else 'Edit Project'}"
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
        self.create_field(parent, "project_name", "Project Name *", tk.Entry)
        
        # Department dropdown
        self.create_dropdown(parent, "department_id", "Department *", self.get_departments())
        
        # Location dropdown
        self.create_dropdown(parent, "location_id", "Location *", self.get_locations())
        
        # Status dropdown
        status_options = [
            ('Planning', 'PLANNING'),
            ('In Progress', 'IN_PROGRESS'),
            ('Completed', 'COMPLETED'),
            ('On Hold', 'ON_HOLD')
        ]
        self.create_dropdown(parent, "status", "Status *", status_options)
        
        self.create_field(parent, "start_date", "Start Date (YYYY-MM-DD)", tk.Entry)
        self.create_field(parent, "end_date", "End Date (YYYY-MM-DD)", tk.Entry)
    
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
    
    def load_project_data(self):
        """Load existing project data into form"""
        data = self.project_data
        
        if 'project_name' in data:
            self.vars['project_name'].set(data['project_name'])
        
        # Department
        if 'department_id' in data and 'department_id_map' in self.vars:
            for display, value in self.vars['department_id_map'].items():
                if value == data['department_id']:
                    self.vars['department_id'].set(display)
                    break
        
        # Location
        if 'location_id' in data and 'location_id_map' in self.vars:
            for display, value in self.vars['location_id_map'].items():
                if value == data['location_id']:
                    self.vars['location_id'].set(display)
                    break
        
        # Status
        if 'status' in data and 'status_reverse_map' in self.vars:
            display = self.vars['status_reverse_map'].get(data['status'])
            if display:
                self.vars['status'].set(display)
        
        # Dates
        if 'start_date' in data and data['start_date']:
            self.vars['start_date'].set(str(data['start_date']))
        if 'end_date' in data and data['end_date']:
            self.vars['end_date'].set(str(data['end_date']))
    
    def validate_form(self):
        """Validate form fields"""
        errors = {}
        
        # Required: Project Name
        project_name = self.vars['project_name'].get().strip()
        if not project_name:
            errors['project_name'] = "Project name is required"
        elif len(project_name) < 3:
            errors['project_name'] = "Project name must be at least 3 characters"
        
        # Required: Department
        dept = self.vars['department_id'].get().strip()
        if not dept:
            errors['department_id'] = "Department is required"
        
        # Required: Location
        location = self.vars['location_id'].get().strip()
        if not location:
            errors['location_id'] = "Location is required"
        
        # Date validation
        start_date_str = self.vars.get('start_date', tk.StringVar()).get().strip()
        end_date_str = self.vars.get('end_date', tk.StringVar()).get().strip()
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                errors['start_date'] = "Invalid date format (use YYYY-MM-DD)"
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                errors['end_date'] = "Invalid date format (use YYYY-MM-DD)"
        
        # Check end date is after start date
        if start_date and end_date and end_date < start_date:
            errors['end_date'] = "End date must be after start date"
        
        # Display errors
        for field, error_msg in errors.items():
            if field in self.error_labels:
                self.error_labels[field].config(text=f"⚠️ {error_msg}")
        
        # Clear errors for valid fields
        for field in self.error_labels:
            if field not in errors:
                self.error_labels[field].config(text="")
        
        return len(errors) == 0
    
    def save_project(self):
        """Save project to database"""
        if not self.validate_form():
            messagebox.showerror("Validation Error", "Please fix the errors before saving.")
            return
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Extract form data
            project_name = self.vars['project_name'].get().strip()
            
            dept_display = self.vars['department_id'].get()
            department_id = self.vars['department_id_map'].get(dept_display)
            
            loc_display = self.vars['location_id'].get()
            location_id = self.vars['location_id_map'].get(loc_display)
            
            status_display = self.vars['status'].get()
            status = self.vars['status_map'].get(status_display)
            
            start_date = self.vars.get('start_date', tk.StringVar()).get().strip() or None
            end_date = self.vars.get('end_date', tk.StringVar()).get().strip() or None
            
            if self.mode == 'add':
                # Insert new project
                cursor.execute("""
                    INSERT INTO projects (project_name, department_id, location_id, status, start_date, end_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (project_name, department_id, location_id, status, start_date, end_date))
                
                conn.commit()
                messagebox.showinfo("Success", f"Project '{project_name}' added successfully!")
            
            else:  # Edit mode
                project_id = self.project_data['project_id']
                
                # Update project
                cursor.execute("""
                    UPDATE projects 
                    SET project_name = %s, department_id = %s, location_id = %s, 
                        status = %s, start_date = %s, end_date = %s
                    WHERE project_id = %s
                """, (project_name, department_id, location_id, status, start_date, end_date, project_id))
                
                conn.commit()
                messagebox.showinfo("Success", f"Project '{project_name}' updated successfully!")
            
            conn.close()
            self.result = True
            self.dialog.destroy()
            
        except pymysql.IntegrityError as e:
            messagebox.showerror("Error", f"Database constraint violation: {e}\n\nProject name might already exist.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project: {e}")
