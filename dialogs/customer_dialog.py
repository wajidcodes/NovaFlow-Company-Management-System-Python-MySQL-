import tkinter as tk
from tkinter import ttk, messagebox
import pymysql

class CustomerDialog:
    def __init__(self, parent, mode='add', customer_data=None, current_user=None, db_connection_func=None):
        """
        Customer Add/Edit Dialog
        
        Args:
            parent: Parent window
            mode: 'add' or 'edit'
            customer_data: Dictionary with customer data (for edit mode)
            current_user: Current logged-in user dict
            db_connection_func: Function to get DB connection
        """
        self.parent = parent
        self.mode = mode
        self.customer_data = customer_data or {}
        self.current_user = current_user
        self.get_db_connection = db_connection_func
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Add New' if mode == 'add' else 'Edit'} Customer")
        
        # Set dialog size
        dialog_width = 600
        dialog_height = 500
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
        if mode == 'edit' and customer_data:
            self.load_customer_data()
    
    def create_ui(self):
        """Create the form UI"""
        # Buttons packed first at bottom to ensure visibility
        btn_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        btn_frame.pack(fill='x', side='bottom', padx=20, pady=20)
        
        tk.Button(btn_frame, text="💾 Save", font=('Segoe UI', 11, 'bold'),
                 bg='#10b981', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.save_customer).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", font=('Segoe UI', 11),
                 bg='#6b7280', fg='white', width=15, height=2, bd=0,
                 cursor='hand2', command=self.dialog.destroy).pack(side='right', padx=5)

        # Container (packed after buttons with expand=True)
        container = tk.Frame(self.dialog, bg='white', bd=0)
        container.pack(fill='both', expand=True, padx=20, pady=(20, 0))
        
        # Header
        header = tk.Frame(container, bg='#0891b2', height=60)
        header.pack(fill='x', pady=(0, 20))
        
        icon = '👥' if self.mode == 'add' else '✏️'
        title = f"{icon} {'Add New Customer' if self.mode == 'add' else 'Edit Customer'}"
        tk.Label(header, text=title, font=('Segoe UI', 16, 'bold'),
                bg='#0891b2', fg='white').pack(pady=15)
        
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
        self.create_field(parent, "name", "Customer Name *", tk.Entry)
        
        # Email
        self.create_field(parent, "email", "Email", tk.Entry)
        
        # Phone
        self.create_field(parent, "phone", "Phone", tk.Entry)
        
        # Address (Text widget)
        addr_frame = tk.Frame(parent, bg='white')
        addr_frame.pack(fill='x', pady=8)
        
        tk.Label(addr_frame, text="Address", font=('Segoe UI', 10),
                bg='white', fg='#475569').pack(anchor='w')
        
        self.addr_text = tk.Text(addr_frame, font=('Segoe UI', 10), bg='#f8fafc',
                                fg='#1e293b', relief='solid', bd=1, height=3, wrap='word')
        self.addr_text.pack(fill='x', pady=(3, 0))
    
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
    
    def load_customer_data(self):
        """Load existing customer data into form"""
        data = self.customer_data
        
        if 'name' in data:
            self.vars['name'].set(data['name'])
        
        if 'email' in data and data['email']:
            self.vars['email'].set(data['email'])
        
        if 'phone' in data and data['phone']:
            self.vars['phone'].set(data['phone'])
        
        if 'address' in data and data['address']:
            self.addr_text.insert('1.0', data['address'])
    
    def validate_form(self):
        """Validate form fields"""
        errors = {}
        
        # Required: Name
        name = self.vars['name'].get().strip()
        if not name:
            errors['name'] = "Customer name is required"
        elif len(name) < 2:
            errors['name'] = "Name must be at least 2 characters"
        
        # Display errors
        for field, error_msg in errors.items():
            if field in self.error_labels:
                self.error_labels[field].config(text=f"⚠️ {error_msg}")
        
        # Clear errors for valid fields
        for field in self.error_labels:
            if field not in errors:
                self.error_labels[field].config(text="")
        
        return len(errors) == 0
    
    def save_customer(self):
        """Save customer to database"""
        if not self.validate_form():
            messagebox.showerror("Validation Error", "Please fix the errors before saving.")
            return
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Extract form data
            name = self.vars['name'].get().strip()
            email = self.vars['email'].get().strip() or None
            phone = self.vars['phone'].get().strip() or None
            address = self.addr_text.get('1.0', 'end-1c').strip() or None
            
            # Auto-assign fields based on current user
            salesman_id = self.current_user['person_id']
            department_id = self.current_user['department_id']
            
            if self.mode == 'add':
                # Insert new customer
                cursor.execute("""
                    INSERT INTO customers (name, email, phone, address, salesman_id, department_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, email, phone, address, salesman_id, department_id))
                
                conn.commit()
                messagebox.showinfo("Success", f"Customer '{name}' added successfully!")
            
            else:  # Edit mode
                customer_id = self.customer_data['customer_id']
                
                # Update customer
                cursor.execute("""
                    UPDATE customers 
                    SET name = %s, email = %s, phone = %s, address = %s
                    WHERE customer_id = %s
                """, (name, email, phone, address, customer_id))
                
                conn.commit()
                messagebox.showinfo("Success", f"Customer '{name}' updated successfully!")
            
            conn.close()
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save customer: {e}")
