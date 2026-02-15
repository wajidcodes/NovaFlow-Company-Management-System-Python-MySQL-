import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
from datetime import datetime, time

class WorkLogDialog:
    def __init__(self, parent, mode='add', worklog_data=None, current_user=None, db_connection_func=None):
        """
        Work Log Add/Edit Dialog
        
        Args:
            parent: Parent window
            mode: 'add' or 'edit'
            worklog_data: Dictionary with work log data (for edit mode)
            current_user: Current logged-in user dict
            db_connection_func: Function to get DB connection
        """
        self.parent = parent
        self.mode = mode
        self.worklog_data = worklog_data or {}
        self.current_user = current_user
        self.get_db_connection = db_connection_func
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Submit' if mode == 'add' else 'Edit'} Work Hours")
        
        # Set dialog size
        dialog_width = 700
        dialog_height = 600
        self.dialog.geometry(f"{dialog_width}x{dialog_height}")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.resizable(True, True)  # Allow resizing
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
        if mode == 'edit' and worklog_data:
            self.load_worklog_data()
        
        # Update total hours when times change
        if mode == 'add':
            self.vars['start_time'].trace('w', lambda *args: self.calculate_hours())
            self.vars['end_time'].trace('w', lambda *args: self.calculate_hours())
    
    def create_ui(self):
        """Create the scrollable form UI"""
        # Buttons packed first at bottom to ensure visibility
        btn_frame = tk.Frame(self.dialog, bg='white', bd=0)
        btn_frame.pack(fill='x', side='bottom', padx=20, pady=20)
        
        btn_inner = tk.Frame(btn_frame, bg='white')
        btn_inner.pack(fill='x')

        tk.Button(btn_inner, text="💾 Submit", font=('Segoe UI', 11, 'bold'),
                 bg='#10b981', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.save_worklog).pack(side='left', padx=5)
        
        tk.Button(btn_inner, text="❌ Cancel", font=('Segoe UI', 11),
                 bg='#6b7280', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.dialog.destroy).pack(side='right', padx=5)

        # Main container with scrollbar
        main_container = tk.Frame(self.dialog, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True, padx=20, pady=(20, 0))

        # Canvas for scrolling
        canvas = tk.Canvas(main_container, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        # Scrollable frame inside canvas
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Link scrollbar to canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ensure frame expands with window
        def on_canvas_configure(event):
            canvas.itemconfig(canvas.find_all()[0], width=event.width)
            
        canvas.bind("<Configure>", on_canvas_configure)

        container = tk.Frame(scrollable_frame, bg='white', bd=0)
        container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Header
        header = tk.Frame(container, bg='#0f172a', height=60)
        header.pack(fill='x', pady=(0, 20))
        
        icon = '⏰' if self.mode == 'add' else '✏️'
        title = f"{icon} {'Submit Work Hours' if self.mode == 'add' else 'Edit Work Log'}"
        tk.Label(header, text=title, font=('Segoe UI', 16, 'bold'),
                bg='#0f172a', fg='white').pack(pady=15)
        
        # Form fields
        form_frame = tk.Frame(container, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Project dropdown
        self.create_dropdown(form_frame, "project_id", "Project *", self.get_user_projects())
        
        # Work Date
        self.create_field(form_frame, "work_date", "Work Date (YYYY-MM-DD) *", tk.Entry)
        
        # Start Time
        self.create_field(form_frame, "start_time", "Start Time (HH:MM) *", tk.Entry)
        
        # End Time
        self.create_field(form_frame, "end_time", "End Time (HH:MM) *", tk.Entry)
        
        # Total Hours (auto-calculated, read-only)
        hours_frame = tk.Frame(form_frame, bg='white')
        hours_frame.pack(fill='x', pady=8)
        
        tk.Label(hours_frame, text="Total Hours (auto-calculated)", font=('Segoe UI', 10),
                bg='white', fg='#475569').pack(anchor='w')
        
        self.total_hours_label = tk.Label(hours_frame, text="0.00 hours", 
                                          font=('Segoe UI', 14, 'bold'), bg='#e0f2fe', 
                                          fg='#0369a1', pady=8, anchor='w', padx=10)
        self.total_hours_label.pack(fill='x', pady=(3, 0))
        
        # Notes (Text widget)
        notes_frame = tk.Frame(form_frame, bg='white')
        notes_frame.pack(fill='x', pady=8)
        
        tk.Label(notes_frame, text="Work Description / Notes", font=('Segoe UI', 10),
                bg='white', fg='#475569').pack(anchor='w')
        
        self.notes_text = tk.Text(notes_frame, font=('Segoe UI', 10), bg='#f8fafc',
                                 fg='#1e293b', relief='solid', bd=1, height=4, wrap='word')
        self.notes_text.pack(fill='x', pady=(3, 0))
        
    
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
    
    def get_user_projects(self):
        """Fetch projects assigned to current user"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            user_id = self.current_user['person_id']
            
            # Get projects where user is assigned
            cursor.execute("""
                SELECT DISTINCT p.project_id, p.project_name
                FROM projects p
                JOIN emp_projects ep ON p.project_id = ep.project_id
                WHERE ep.employee_id = %s AND p.status != 'COMPLETED'
                ORDER BY p.project_name
            """, (user_id,))
            
            projects = cursor.fetchall()
            conn.close()
            
            if not projects:
                return [("No projects assigned", None)]
            
            return [(proj['project_name'], proj['project_id']) for proj in projects]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load projects: {e}")
            return [("Error loading projects", None)]
    
    def calculate_hours(self):
        """Calculate total hours from start and end time"""
        try:
            start_str = self.vars['start_time'].get().strip()
            end_str = self.vars['end_time'].get().strip()
            
            if not start_str or not end_str:
                return
            
            # Parse times
            start_parts = start_str.split(':')
            end_parts = end_str.split(':')
            
            if len(start_parts) != 2 or len(end_parts) != 2:
                return
            
            start_hour, start_min = int(start_parts[0]), int(start_parts[1])
            end_hour, end_min = int(end_parts[0]), int(end_parts[1])
            
            # Calculate difference in minutes
            start_total_mins = start_hour * 60 + start_min
            end_total_mins = end_hour * 60 + end_min
            
            diff_mins = end_total_mins - start_total_mins
            
            if diff_mins < 0:
                diff_mins += 24 * 60  # Handle overnight shift
            
            total_hours = diff_mins / 60.0
            self.total_hours_label.config(text=f"{total_hours:.2f} hours")
            
        except (ValueError, IndexError):
            pass
    
    def load_worklog_data(self):
        """Load existing work log data into form"""
        data = self.worklog_data
        
        # Project
        if 'project_id' in data and 'project_id_map' in self.vars:
            for display, value in self.vars['project_id_map'].items():
                if value == data['project_id']:
                    self.vars['project_id'].set(display)
                    break
        
        # Dates and times
        if 'work_date' in data and data['work_date']:
            self.vars['work_date'].set(str(data['work_date']))
        
        if 'start_time' in data and data['start_time']:
            # Convert time object to string
            start_time = data['start_time']
            if isinstance(start_time, str):
                self.vars['start_time'].set(start_time)
            else:
                self.vars['start_time'].set(start_time.strftime('%H:%M'))
        
        if 'end_time' in data and data['end_time']:
            end_time = data['end_time']
            if isinstance(end_time, str):
                self.vars['end_time'].set(end_time)
            else:
                self.vars['end_time'].set(end_time.strftime('%H:%M'))
        
        # Notes
        if 'notes' in data and data['notes']:
            self.notes_text.insert('1.0', data['notes'])
        
        # Calculate hours
        self.calculate_hours()
    
    def validate_form(self):
        """Validate form fields"""
        errors = {}
        
        # Required: Project
        project = self.vars['project_id'].get().strip()
        if not project or project == "No projects assigned":
            errors['project_id'] = "Please select a project"
        
        # Required: Work Date
        work_date_str = self.vars['work_date'].get().strip()
        if not work_date_str:
            errors['work_date'] = "Work date is required"
        else:
            try:
                datetime.strptime(work_date_str, '%Y-%m-%d')
            except ValueError:
                errors['work_date'] = "Invalid date format (use YYYY-MM-DD)"
        
        # Required: Start Time
        start_time_str = self.vars['start_time'].get().strip()
        if not start_time_str:
            errors['start_time'] = "Start time is required"
        else:
            try:
                parts = start_time_str.split(':')
                if len(parts) != 2:
                    raise ValueError
                hour, minute = int(parts[0]), int(parts[1])
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError
            except (ValueError, IndexError):
                errors['start_time'] = "Invalid time format (use HH:MM, e.g., 09:00)"
        
        # Required: End Time
        end_time_str = self.vars['end_time'].get().strip()
        if not end_time_str:
            errors['end_time'] = "End time is required"
        else:
            try:
                parts = end_time_str.split(':')
                if len(parts) != 2:
                    raise ValueError
                hour, minute = int(parts[0]), int(parts[1])
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError
            except (ValueError, IndexError):
                errors['end_time'] = "Invalid time format (use HH:MM, e.g., 17:00)"
        
        # Display errors
        for field, error_msg in errors.items():
            if field in self.error_labels:
                self.error_labels[field].config(text=f"⚠️ {error_msg}")
        
        # Clear errors for valid fields
        for field in self.error_labels:
            if field not in errors:
                self.error_labels[field].config(text="")
        
        return len(errors) == 0
    
    def save_worklog(self):
        """Save work log to database"""
        if not self.validate_form():
            messagebox.showerror("Validation Error", "Please fix the errors before submitting.")
            return
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Extract form data
            project_display = self.vars['project_id'].get()
            project_id = self.vars['project_id_map'].get(project_display)
            
            if not project_id:
                messagebox.showerror("Error", "Invalid project selected")
                return
            
            work_date = self.vars['work_date'].get().strip()
            start_time_str = self.vars['start_time'].get().strip()
            end_time_str = self.vars['end_time'].get().strip()
            notes = self.notes_text.get('1.0', 'end-1c').strip() or None
            
            employee_id = self.current_user['person_id']
            
            if self.mode == 'add':
                # Insert new work log (total_hours will be calculated by trigger)
                cursor.execute("""
                    INSERT INTO work_log (employee_id, project_id, work_date, start_time, end_time, notes, approval_status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'PENDING')
                """, (employee_id, project_id, work_date, start_time_str, end_time_str, notes))
                
                conn.commit()
                messagebox.showinfo("Success", "Work hours submitted successfully!\n\nStatus: Pending Supervisor Approval")
            
            else:  # Edit mode
                log_id = self.worklog_data['log_id']
                
                # Update work log
                cursor.execute("""
                    UPDATE work_log 
                    SET project_id = %s, work_date = %s, start_time = %s, end_time = %s, notes = %s
                    WHERE log_id = %s
                """, (project_id, work_date, start_time_str, end_time_str, notes, log_id))
                
                conn.commit()
                messagebox.showinfo("Success", "Work log updated successfully!")
            
            conn.close()
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save work log: {e}")
