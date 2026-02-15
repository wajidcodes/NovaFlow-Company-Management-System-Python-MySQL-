"""
Report View - Dashboard with metrics and reports
"""
import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView
from services.report_service import ReportService
from utils.constants import COLORS, has_permission, PersonType


class ReportView(BaseView):
    """Reports and Dashboard View"""
    
    def create_ui(self):
        self.service = ReportService()
        
        # Header
        self.create_header("📊 Dashboard & Reports")
        
        # Metrics Cards
        self.create_metrics_section()
        
        # Report Section
        self.create_report_section()
    
    def create_metrics_section(self):
        """Create dashboard metrics cards"""
        metrics_frame = tk.Frame(self.frame, bg='white')
        metrics_frame.pack(fill='x', padx=20, pady=20)
        
        # Get metrics from service
        try:
            metrics = self.service.get_dashboard_metrics()
        except Exception as e:
            metrics = {
                'total_orders': 0,
                'total_revenue': 0,
                'total_customers': 0,
                'low_stock_count': 0
            }
        
        # Create cards
        cards_data = [
            ("📦 Total Orders", metrics.get('total_orders', 0), COLORS['primary']),
            ("💰 Revenue", f"PKR {metrics.get('total_revenue', 0):,.0f}", COLORS['success']),
            ("👥 Customers", metrics.get('total_customers', 0), COLORS['info']),
            ("⚠️ Low Stock", metrics.get('low_stock_count', 0), COLORS['warning']),
        ]
        
        for i, (label, value, color) in enumerate(cards_data):
            card = tk.Frame(metrics_frame, bg=color, padx=20, pady=15)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
            
            tk.Label(card, text=label, font=('Arial', 11), 
                    bg=color, fg='white').pack(anchor='w')
            tk.Label(card, text=str(value), font=('Arial', 22, 'bold'), 
                    bg=color, fg='white').pack(anchor='w', pady=(5, 0))
        
        # Configure grid columns to expand equally
        for i in range(4):
            metrics_frame.columnconfigure(i, weight=1)
    
    def create_report_section(self):
        """Create report generation section"""
        report_frame = tk.Frame(self.frame, bg=COLORS['bg_light'])
        report_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Toolbar
        toolbar = tk.Frame(report_frame, bg=COLORS['bg_light'])
        toolbar.pack(fill='x', pady=10)
        
        tk.Label(toolbar, text="Report Type:", bg=COLORS['bg_light'], 
                font=('Arial', 11)).pack(side='left', padx=(10, 5))
        
        self.report_type = tk.StringVar(value='Top Salesmen')
        types = ['Top Salesmen', 'Low Stock Items', 'Order Summary']
        cb = ttk.Combobox(toolbar, textvariable=self.report_type, values=types, 
                         state='readonly', width=20)
        cb.pack(side='left', padx=5)
        
        tk.Button(toolbar, text="Generate", command=self.generate_report,
                 bg=COLORS['primary'], fg='white', padx=15, pady=5, bd=0,
                 cursor='hand2').pack(side='left', padx=10)
        
        # Report display area
        self.report_display = tk.Frame(report_frame, bg='white')
        self.report_display.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(self.report_display, text="Select a report type and click Generate",
                bg='white', fg=COLORS['text_muted'], font=('Arial', 12)).pack(expand=True)
    
    def generate_report(self):
        """Generate the selected report"""
        # Clear previous
        for widget in self.report_display.winfo_children():
            widget.destroy()
        
        report_type = self.report_type.get()
        
        try:
            if report_type == 'Top Salesmen':
                self.show_top_salesmen()
            elif report_type == 'Low Stock Items':
                self.show_low_stock()
            elif report_type == 'Order Summary':
                self.show_order_summary()
        except Exception as e:
            tk.Label(self.report_display, text=f"Error: {e}", 
                    bg='white', fg=COLORS['danger']).pack(expand=True)
    
    def show_top_salesmen(self):
        """Display top salesmen report"""
        tk.Label(self.report_display, text="🏆 Top Salesmen", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        data = self.service.get_top_salesmen(5)
        
        if not data:
            tk.Label(self.report_display, text="No data available", 
                    bg='white', fg=COLORS['text_muted']).pack()
            return
        
        # Create simple table
        columns = ('Rank', 'Name', 'Orders', 'Revenue')
        tree = ttk.Treeview(self.report_display, columns=columns, show='headings', height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        for i, row in enumerate(data, 1):
            tree.insert('', 'end', values=(
                i,
                row.get('name', 'Unknown'),
                row.get('order_count', 0),
                f"PKR {row.get('total_sales', 0):,.0f}"
            ))
        
        tree.pack(fill='x', padx=20, pady=10)
    
    def show_low_stock(self):
        """Display low stock items"""
        tk.Label(self.report_display, text="⚠️ Low Stock Items", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        data = self.service.get_low_stock_items(10)
        
        if not data:
            tk.Label(self.report_display, text="All items have sufficient stock!", 
                    bg='white', fg=COLORS['success']).pack()
            return
        
        columns = ('Product', 'Warehouse', 'Current Stock', 'Reorder Level')
        tree = ttk.Treeview(self.report_display, columns=columns, show='headings', height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        for row in data:
            tree.insert('', 'end', values=(
                row.get('product_name', 'Unknown'),
                row.get('warehouse_name', 'Unknown'),
                row.get('qty', 0),
                row.get('reorder_level', 10)
            ))
        
        tree.pack(fill='x', padx=20, pady=10)
    
    def show_order_summary(self):
        """Display order summary"""
        tk.Label(self.report_display, text="📋 Order Summary", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=10)
        
        metrics = self.service.get_dashboard_metrics()
        
        summary = f"""
        Total Orders: {metrics.get('total_orders', 0)}
        Total Revenue: PKR {metrics.get('total_revenue', 0):,.0f}
        Total Customers: {metrics.get('total_customers', 0)}
        """
        
        tk.Label(self.report_display, text=summary, font=('Arial', 12),
                bg='white', justify='left').pack(pady=10)
