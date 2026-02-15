"""
Dashboard View

Main application shell containing sidebar navigation and content area.
Handles routing between different modules.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLORS, PersonType, has_permission
from utils.logger import setup_logger

# Import Views
from views.employee_view import EmployeeView
from views.department_view import DepartmentView
from views.project_view import ProjectView
from views.warehouse_view import WarehouseView
from views.product_view import ProductView
from views.customer_view import CustomerView
from views.order_view import OrderView
from views.worklog_view import WorkLogView
from views.report_view import ReportView

logger = setup_logger(__name__)


class DashboardView:
    """Main Dashboard Container"""
    
    def __init__(self, root, current_user, logout_callback):
        self.root = root
        self.current_user = current_user
        self.logout_callback = logout_callback
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the dashboard layout - Full Height Sidebar"""
        # Main Layout: 2 Columns
        # Col 0: Sidebar (Full Height)
        # Col 1: Main Content Area (Top Bar + Content)
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Sidebar Container
        sidebar_container = tk.Frame(self.root, bg=COLORS['bg_card'], width=240)
        sidebar_container.grid(row=0, column=0, sticky='nsew')
        sidebar_container.grid_propagate(False) # Maintain width
        
        self.create_sidebar(sidebar_container)
        
        # Main Content Area Container
        main_right_panel = tk.Frame(self.root, bg=COLORS['bg_light'])
        main_right_panel.grid(row=0, column=1, sticky='nsew')
        
        # Top Bar (Inside Right Panel)
        self.create_top_bar(main_right_panel)
        
        # Content Wrapper
        content_wrapper = tk.Frame(main_right_panel, bg=COLORS['bg_light'], padx=20, pady=20)
        content_wrapper.pack(fill='both', expand=True)
        
        # Actual Content Area
        self.content_area = tk.Frame(content_wrapper, bg='white')
        self.content_area.pack(fill='both', expand=True)
        
        # Add shadow/border effect to content area
        self.content_area.config(highlightbackground='#e2e8f0', highlightthickness=1)
        
        # Show default view based on role
        self.show_default_view()
        
    def create_top_bar(self, parent):
        """Create the top navigation bar"""
        top_bar = tk.Frame(parent, bg='white', height=60)
        top_bar.pack(fill='x')
        
        # Shadow border for top bar
        invalid_frame = tk.Frame(parent, bg='#e2e8f0', height=1)
        invalid_frame.pack(fill='x')
        
        # User Info (Right aligned)
        user_info = f"{self.current_user['name']} | {PersonType.display_name(PersonType(self.current_user['person_type']))}"
        
        # User Avatar Placeholder (Circle)
        avatar_frame = tk.Frame(top_bar, bg=COLORS['primary'], width=35, height=35)
        # avatar_frame.pack(side='right', padx=20, pady=12) # Placeholder
         
        tk.Label(top_bar, text=user_info, 
                font=('Segoe UI', 11), bg='white', fg=COLORS['text_muted']).pack(side='right', padx=20, pady=15)

    def create_sidebar(self, parent):
        """Create sidebar content"""
        # Logo Area
        logo_frame = tk.Frame(parent, bg=COLORS['bg_dark'], height=60)
        logo_frame.pack(fill='x')
        logo_frame.pack_propagate(False)
        
        tk.Label(logo_frame, text="✨ NovaFlow", 
                font=('Segoe UI', 16, 'bold'), bg=COLORS['bg_dark'], fg='white').pack(expand=True)
        
        self.nav_buttons = {}
        
        # Menu Scroll Frame (if needed, but keeping simple for now)
        menu_frame = tk.Frame(parent, bg=COLORS['bg_card'])
        menu_frame.pack(fill='both', expand=True, pady=10)
        
        # Menu Header
        tk.Label(menu_frame, text="MAIN MENU", font=('Segoe UI', 9, 'bold'), 
                bg=COLORS['bg_card'], fg='#64748b', anchor='w').pack(fill='x', padx=20, pady=(20, 10))
        
        # Navigation Items
        self.add_nav_item(menu_frame, "Dashboard", "📊", self.show_reports)
        
        user = self.current_user
        if has_permission(user, 'view_employees'):
            self.add_nav_item(menu_frame, "Employees", "👥", self.show_employees)
        if has_permission(user, 'view_departments'):
            self.add_nav_item(menu_frame, "Departments", "🏢", self.show_departments)
        if has_permission(user, 'view_projects'):
            self.add_nav_item(menu_frame, "Projects", "📋", self.show_projects)
        if has_permission(user, 'view_warehouses'):
             self.add_nav_item(menu_frame, "Warehouses", "🏭", self.show_warehouses)
        if has_permission(user, 'view_products'):
             self.add_nav_item(menu_frame, "Products", "📦", self.show_products)
        if has_permission(user, 'view_customers'):
            self.add_nav_item(menu_frame, "Customers", "🤝", self.show_customers)
        if has_permission(user, 'view_orders'):
            self.add_nav_item(menu_frame, "Orders", "🛒", self.show_orders)
            
        self.add_nav_item(menu_frame, "Work Logs", "⏰", self.show_work_logs)
        
        # Logout Area (at bottom)
        logout_btn = tk.Button(parent, text="🚪  Logout", font=('Segoe UI', 10), 
                 bg='#ef4444', fg='white', width=20, pady=10, bd=0,
                 cursor='hand2', command=self.logout_callback)
        logout_btn.pack(side='bottom', fill='x', padx=20, pady=20)
        
        # Hover for logout
        logout_btn.bind('<Enter>', lambda e: logout_btn.config(bg='#dc2626'))
        logout_btn.bind('<Leave>', lambda e: logout_btn.config(bg='#ef4444'))
                 
    def add_nav_item(self, parent, text, icon, command):
        """Create a styled navigation button with icon"""
        btn_text = f"  {icon}   {text}"
        
        btn = tk.Button(parent, text=btn_text, font=('Segoe UI', 10), 
                       bg=COLORS['bg_card'], fg='#e2e8f0', bd=0,
                       cursor='hand2', anchor='w', padx=20, pady=10,
                       activebackground=COLORS['bg_dark'], activeforeground='white',
                       command=lambda: self.handle_nav_click(text, command))
        btn.pack(fill='x', padx=10, pady=2)
        
        self.nav_buttons[text] = btn
        
        # Hover effect handling (only if not active)
        btn.bind('<Enter>', lambda e: self.on_hover(text))
        btn.bind('<Leave>', lambda e: self.on_leave(text))
        
    def handle_nav_click(self, name, command):
        """Update active state and execute command"""
        # Reset all buttons
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.config(bg=COLORS['primary'], fg='white', font=('Segoe UI', 10, 'bold'))
            else:
                btn.config(bg=COLORS['bg_card'], fg='#e2e8f0', font=('Segoe UI', 10))
                
        # Execute view change
        command()
        
    def on_hover(self, name):
        """Hover effect"""
        btn = self.nav_buttons[name]
        if btn['bg'] != COLORS['primary']: # Don't change if active
            btn.config(bg=COLORS['bg_dark'], fg='white')
            
    def on_leave(self, name):
        """Leave effect"""
        btn = self.nav_buttons[name]
        if btn['bg'] != COLORS['primary']: # Don't change if active
            btn.config(bg=COLORS['bg_card'], fg='#e2e8f0')

    def show_employees(self):
        self.current_view = EmployeeView(self.content_area, self.current_user)
        
    def show_departments(self):
        self.current_view = DepartmentView(self.content_area, self.current_user)
        
    def show_projects(self):
        self.current_view = ProjectView(self.content_area, self.current_user)
        
    def show_warehouses(self):
        self.current_view = WarehouseView(self.content_area, self.current_user)
        
    def show_products(self):
        self.current_view = ProductView(self.content_area, self.current_user)
        
    def show_customers(self):
        self.current_view = CustomerView(self.content_area, self.current_user)
        
    def show_orders(self):
        self.current_view = OrderView(self.content_area, self.current_user)
        
    def show_work_logs(self):
        self.current_view = WorkLogView(self.content_area, self.current_user)
        
    def show_reports(self):
        self.current_view = ReportView(self.content_area, self.current_user)
        
    def show_default_view(self):
        """Determine default view based on role"""
        user_type = PersonType(self.current_user['person_type'])
        
        if user_type == PersonType.SALESMAN:
            self.handle_nav_click("Orders", self.show_orders)
        elif user_type == PersonType.GENERAL_EMPLOYEE:
            self.handle_nav_click("Work Logs", self.show_work_logs)
        else:
            self.handle_nav_click("Dashboard", self.show_reports)
