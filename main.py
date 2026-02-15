"""
SpaceX Company Management System
Main Application Entry Point

Refactored to use MVC-like architecture.
"""
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv

from config.database import get_db_connection
from utils.logger import setup_logger
from services.auth_service import AuthService
from views.dashboard_view import DashboardView
from dialogs.login import LoginWindow
from Style.theme_manager import ThemeManager

# Setup logging
logger = setup_logger(__name__)

# Load environment variables
load_dotenv()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("NovaFlow Enterprise Systems")
        self.root.state('zoomed')
        
        # Apply Theme
        ThemeManager.apply_theme(self.root)
        
        # Services
        self.auth_service = AuthService()
        
        # State
        self.current_user = None
        
        # Start with Login
        self.show_login()

    def show_login(self):
        """Display login screen"""
        self.clear_root()
        self.login_view = LoginWindow(self.root, self.on_login_success)

    def on_login_success(self, user_data):
        """Handle successful login"""
        self.current_user = user_data
        logger.info(f"User logged in: {user_data['email']}")
        self.show_dashboard()

    def show_dashboard(self):
        """Display main dashboard"""
        self.clear_root()
        # Initialize Dashboard View
        DashboardView(self.root, self.current_user, self.logout)

    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            logger.info(f"User logged out: {self.current_user['email']}")
            self.current_user = None
            self.show_login()

    def clear_root(self):
        """Clear all widgets from root"""
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        messagebox.showerror("Critical Error", f"Application crashed: {e}")