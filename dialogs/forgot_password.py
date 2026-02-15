import tkinter as tk
from tkinter import messagebox
from services.auth_service import get_auth_service

class ForgotPasswordDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reset Password - NovaFlow")
        self.geometry("450x550")
        self.configure(bg="#1e293b")
        self.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # UI Setup
        self.create_ui()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_ui(self):
        # Header
        tk.Label(self, text="🔑", font=("Segoe UI Emoji", 40), 
                bg="#1e293b").pack(pady=(40, 10))
        
        tk.Label(self, text="Forgot Password?", font=("Segoe UI", 24, "bold"), 
                bg="#1e293b", fg="white").pack()
        
        tk.Label(self, text="Enter your email to verify account", 
                font=("Segoe UI", 10), bg="#1e293b", fg="#94a3b8").pack(pady=(5, 30))
        
        # Content Frame
        self.content_frame = tk.Frame(self, bg="#1e293b")
        self.content_frame.pack(fill='x', padx=50)
        
        # Initial State: Email Entry
        self.setup_email_step()
        
    def setup_email_step(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="Email Address", font=("Segoe UI", 10, "bold"), 
                bg="#1e293b", fg="#e2e8f0").pack(anchor='w', pady=(0, 5))
        
        self.email_var = tk.StringVar()
        entry = tk.Entry(self.content_frame, textvariable=self.email_var, 
                        font=("Segoe UI", 11), bg="#334155", fg="white", 
                        relief='flat', insertbackground="white")
        entry.pack(fill='x', ipady=8, pady=(0, 20))
        entry.focus()
        
        verify_btn = tk.Button(self.content_frame, text="Verify Account", 
                              font=("Segoe UI", 11, "bold"),
                              bg="#3b82f6", fg="white", bd=0, cursor="hand2",
                              activebackground="#2563eb", activeforeground="white",
                              command=self.verify_email)
        verify_btn.pack(fill='x', ipady=10)
        
    def setup_password_step(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="New Password", font=("Segoe UI", 10, "bold"), 
                bg="#1e293b", fg="#e2e8f0").pack(anchor='w', pady=(0, 5))
        
        self.new_pass_var = tk.StringVar()
        pass_entry = tk.Entry(self.content_frame, textvariable=self.new_pass_var, 
                             font=("Segoe UI", 11), bg="#334155", fg="white", 
                             relief='flat', insertbackground="white", show="•")
        pass_entry.pack(fill='x', ipady=8, pady=(0, 15))
        pass_entry.focus()
        
        tk.Label(self.content_frame, text="Confirm Password", font=("Segoe UI", 10, "bold"), 
                bg="#1e293b", fg="#e2e8f0").pack(anchor='w', pady=(0, 5))
        
        self.confirm_pass_var = tk.StringVar()
        confirm_entry = tk.Entry(self.content_frame, textvariable=self.confirm_pass_var, 
                                font=("Segoe UI", 11), bg="#334155", fg="white", 
                                relief='flat', insertbackground="white", show="•")
        confirm_entry.pack(fill='x', ipady=8, pady=(0, 20))
        
        save_btn = tk.Button(self.content_frame, text="Reset Password", 
                            font=("Segoe UI", 11, "bold"),
                            bg="#22c55e", fg="white", bd=0, cursor="hand2",
                            activebackground="#16a34a", activeforeground="white",
                            command=self.save_password)
        save_btn.pack(fill='x', ipady=10)
        
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def verify_email(self):
        email = self.email_var.get().strip()
        if not email:
            messagebox.showwarning("Input Required", "Please enter your email address.")
            return
            
        # Check if user exists (Quick hack: try to update with dummy password or just SELECT)
        # Better: Add check_user_exists to auth_service. For now, we'll try to just SELECT using raw connection or existing fetch mechanism
        # Actually, let's use a simpler heuristic: If 'authenticate' returns "Invalid email" vs "Invalid password" logic?
        # No, auth service returns same error.
        
        # Let's add 'user_exists' to auth service? 
        # For this lab, I will just assume the user exists if the format is valid, 
        # or I can query DB directly here if I import get_db_connection.
        
        # Let's verify via DB
        from config.database import get_db_connection
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM person WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                self.verified_email = email
                messagebox.showinfo("Success", f"Account found for {user['name']}.\nPlease enter your new password.")
                self.setup_password_step()
            else:
                messagebox.showerror("Error", "No account found with this email address.")
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
        finally:
            conn.close()
            
    def save_password(self):
        new_pass = self.new_pass_var.get()
        confirm_pass = self.confirm_pass_var.get()
        
        if not new_pass or len(new_pass) < 4:
            messagebox.showwarning("Invalid Password", "Password must be at least 4 characters.")
            return
            
        if new_pass != confirm_pass:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return
            
        # Update using AuthService
        auth = get_auth_service()
        if auth.update_password(self.verified_email, new_pass):
            messagebox.showinfo("Success", "Password reset successfully!\nYou can now login.")
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to update password.")
