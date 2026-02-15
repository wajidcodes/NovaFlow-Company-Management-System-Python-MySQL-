from views.base_view import BaseView
import tkinter as tk

class PlaceholderView(BaseView):
    def create_ui(self):
        tk.Label(self.frame, text="🚧 Module Under Construction", 
                font=('Arial', 20)).pack(expand=True)

class DepartmentView(PlaceholderView): pass
class ProjectView(PlaceholderView): pass
class WarehouseView(PlaceholderView): pass
class ProductView(PlaceholderView): pass
class CustomerView(PlaceholderView): pass
class OrderView(PlaceholderView): pass
class WorkLogView(PlaceholderView): pass
class ReportView(PlaceholderView): pass
