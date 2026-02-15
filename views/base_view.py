"""
Base View Class

Provides common functionality for all content views in the dashboard.
Handles standardized layouts, headers, and widget creation helpers.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLORS, DEFAULT_PAGE_SIZE

class BaseView:
    """Base class for all dashboard views"""
    
    def __init__(self, parent, current_user):
        """
        Initialize the view.
        
        Args:
            parent: Parent widget (usually the content area frame)
            current_user: Dict containing logged-in user info
        """
        self.parent = parent
        self.current_user = current_user
        self.root = parent.winfo_toplevel()
        
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
            
        # Main container for this view - "Card" look
        self.frame = tk.Frame(self.parent, bg='white')
        self.frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Add a subtle border/shadow effect via a nested frame if needed, 
        # but pure white card on grey bg is standard modern look.
        
        self.create_ui()
    
    def create_ui(self):
        """Override this method to build the UI"""
        pass
    
    def create_header(self, title, button_text=None, button_command=None):
        """
        Create a standardized header with title and optional action button.
        """
        header_frame = tk.Frame(self.frame, bg='white')
        header_frame.pack(fill='x', padx=20, pady=(20, 20))
        
        # Title
        tk.Label(header_frame, text=title, font=('Arial', 24, 'bold'), 
                bg='white', fg=COLORS['text_dark']).pack(side='left')
        
        # Action Button (e.g. "Add Employee")
        if button_text and button_command:
            btn = tk.Button(header_frame, text=button_text, font=('Arial', 10),
                           bg=COLORS['primary'], fg='white', padx=15, pady=8, bd=0, 
                           cursor='hand2', command=button_command)
            btn.pack(side='right')
            
            # Hover effects
            btn.bind('<Enter>', lambda e: btn.config(bg=COLORS['primary_hover']))
            btn.bind('<Leave>', lambda e: btn.config(bg=COLORS['primary']))
            
            return btn
        return None
    
    def create_button(self, parent, text, command, bg_color):
        """Helper to create standardized buttons"""
        btn = tk.Button(parent, text=text, font=('Segoe UI', 10, 'bold'),
                       bg=bg_color, fg='white', padx=20, pady=8, bd=0,
                       cursor='hand2', command=command)
        btn.pack(side='left', padx=8)
        
        # Hover effect
        def on_enter(e):
            btn.config(relief='sunken')
        def on_leave(e):
            btn.config(relief='flat')
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def create_toolbar(self, search_command=None, filter_options=None):
        """
        Create a standardized toolbar with search and filters.
        """
        toolbar = tk.Frame(self.frame, bg=COLORS['bg_light'], padx=15, pady=10)
        toolbar.pack(fill='x', padx=20)
        
        widgets = {}
        
        # Search Box
        if search_command:
            search_frame = tk.Frame(toolbar, bg=COLORS['bg_light'])
            search_frame.pack(side='left', fill='x', expand=True, padx=(0, 20))
            
            tk.Label(search_frame, text="🔍", bg=COLORS['bg_light'], 
                    font=('Arial', 12)).pack(side='left', padx=10)
            
            search_var = tk.StringVar()
            search_entry = tk.Entry(search_frame, textvariable=search_var, 
                                   font=('Segoe UI', 11), width=50, relief='flat', bd=1)
            search_entry.pack(side='left', fill='x', expand=True, ipady=5) # ipady for height
            search_entry.bind('<Return>', lambda e: search_command())
            
            widgets['search_var'] = search_var
            widgets['search_entry'] = search_entry
            
            # Search Button
            search_btn = tk.Button(search_frame, text="Search", command=search_command,
                     bg=COLORS['primary'], fg='white', bd=0, padx=20, pady=5, cursor='hand2', font=('Segoe UI', 10))
            search_btn.pack(side='left', padx=10)
            
            # Hover for search button
            search_btn.bind('<Enter>', lambda e: search_btn.config(bg=COLORS['primary_hover']))
            search_btn.bind('<Leave>', lambda e: search_btn.config(bg=COLORS['primary']))
        
        # Filters
        if filter_options:
            filter_frame = tk.Frame(toolbar, bg=COLORS['bg_light'])
            filter_frame.pack(side='right')
            
            for label, options, command in filter_options:
                tk.Label(filter_frame, text=label, bg=COLORS['bg_light'], 
                        font=('Arial', 10)).pack(side='left', padx=(15, 5))
                
                var = tk.StringVar(value=options[0])
                cb = ttk.Combobox(filter_frame, textvariable=var, values=options, 
                                 state='readonly', width=15)
                cb.pack(side='left')
                cb.bind('<<ComboboxSelected>>', lambda e, cmd=command: cmd())
                
                widgets[f'filter_{label}'] = var
                widgets[f'cb_{label}'] = cb
        
        return widgets

    def create_treeview(self, columns, parent_frame=None):
        """
        Create a standardized Treeview widget with scrollbar.
        """
        if parent_frame is None:
            parent_frame = tk.Frame(self.frame, bg='white')
            parent_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        tree = ttk.Treeview(parent_frame, columns=columns, show='headings', 
                           yscrollcommand=scrollbar.set, height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)  # Default width
            
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=tree.yview)
        
        # Base styling
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme for better customization support
        style.configure("Treeview.Heading", font=('Segoe UI', 9, 'bold'), 
                       background='#f1f5f9', foreground='#475569', relief='flat', padding=10)
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=40, 
                       background="white", fieldbackground="white", borderwidth=0)
        style.map("Treeview", background=[('selected', COLORS['primary'])], foreground=[('selected', 'white')])
        
        # Tag Configs (Common statuses)
        tree.tag_configure('active', foreground=COLORS['success'])
        tree.tag_configure('inactive', foreground=COLORS['danger'])
        tree.tag_configure('pending', foreground=COLORS['warning'])
        tree.tag_configure('approved', foreground=COLORS['success'])
        tree.tag_configure('rejected', foreground=COLORS['danger'])
        
        return tree

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_success(self, message):
        messagebox.showinfo("Success", message)
        
    def confirm_action(self, title, message):
        return messagebox.askyesno(title, message)
