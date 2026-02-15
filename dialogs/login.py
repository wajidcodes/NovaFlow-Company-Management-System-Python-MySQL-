import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("NovaFlow Enterprise Systems - Login")
        self.root.state('zoomed')
        self.root.configure(bg="white")
        
        self.create_login_ui()
    
    def create_login_ui(self):
        # Main container (Split Screen)
        main_container = tk.Frame(self.root, bg="#0f172a")
        main_container.pack(fill='both', expand=True)
        
        # LEFT PANEL - Login Form (40% width)
        # Use Dark Background
        left_panel = tk.Frame(main_container, bg="#0f172a", width=500)
        left_panel.place(relx=0, rely=0, relwidth=0.4, relheight=1)
        
        # Center container for form
        form_container = tk.Frame(left_panel, bg="#0f172a")
        form_container.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.8)
        
        # Branding
        tk.Label(form_container, text="✨", font=("Segoe UI Emoji", 40), bg="#0f172a").pack(anchor='center')
        tk.Label(form_container, text="NovaFlow", font=("Segoe UI", 36, "bold"), 
                bg="#0f172a", fg="white").pack(anchor='center')
        tk.Label(form_container, text="Enterprise Management System", 
                font=("Segoe UI", 12), bg="#0f172a", fg="#94a3b8").pack(anchor='center', pady=(0, 40))
        
        # Email field
        tk.Label(form_container, text="Email Address", font=("Segoe UI", 10, "bold"), 
                bg="#0f172a", fg="#e2e8f0").pack(anchor='w', pady=(0, 5))
        
        self.email_var = tk.StringVar()
        email_entry = tk.Entry(form_container, textvariable=self.email_var, 
                              font=("Segoe UI", 11), bg="#1e293b", fg="white", 
                              relief='flat', insertbackground="white")
        email_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Password field
        tk.Label(form_container, text="Password", font=("Segoe UI", 10, "bold"), 
                bg="#0f172a", fg="#e2e8f0").pack(anchor='w', pady=(0, 5))
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(form_container, textvariable=self.password_var, 
                                      font=("Segoe UI", 11), bg="#1e293b", fg="white", 
                                      relief='flat', insertbackground="white", show="•")
        self.password_entry.pack(fill='x', pady=(0, 10), ipady=8)
        
        # Options Row (Show Pass | Forgot Pass)
        options_frame = tk.Frame(form_container, bg="#0f172a")
        options_frame.pack(fill='x', pady=(0, 30))
        
        # Show password checkbox
        self.show_pass_var = tk.BooleanVar()
        tk.Checkbutton(options_frame, text="Show Password", variable=self.show_pass_var, 
                      command=self.toggle_password, bg="#0f172a", activebackground="#0f172a", 
                      font=("Segoe UI", 9), fg="#94a3b8", selectcolor="#1e293b", 
                      activeforeground="white", bd=0).pack(side='left')
                      
        # Forgot Password Link
        forgot_btn = tk.Button(options_frame, text="Forgot Password?", 
                             font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#3b82f6", 
                             bd=0, cursor="hand2", activebackground="#0f172a", 
                             activeforeground="#60a5fa", command=self.forgot_password_action)
        forgot_btn.pack(side='right')
        
        # Login button
        login_btn = tk.Button(form_container, text="Sign In", font=("Segoe UI", 11, "bold"),
                             bg="#3b82f6", fg="white", bd=0, cursor="hand2",
                             activebackground="#2563eb", activeforeground="white",
                             command=self.login_action)
        login_btn.pack(fill='x', ipady=10)
        
        # Hover effects
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg="#2563eb"))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg="#3b82f6"))
        
        # RIGHT PANEL - Image (60% width)
        right_panel = tk.Frame(main_container, bg="#f1f5f9")
        right_panel.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)
        
        self.load_background_image(right_panel)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login_action())
        email_entry.focus()
        
    def forgot_password_action(self):
        """Open the forgot password dialog"""
        from dialogs.forgot_password import ForgotPasswordDialog
        ForgotPasswordDialog(self.root)

    def load_background_image(self, parent):
        """Load and display the side image"""
        try:
            # Try loading the new NovaFlow asset
            image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Images", "novaflow_login.png")
            
            if not os.path.exists(image_path):
                # Fallback to older image if new one missing
                image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Images", "spacex.jpg")
            
            if os.path.exists(image_path):
                img = Image.open(image_path)
                
                # Resize to fit right panel
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                target_width = int(screen_width * 0.6)
                
                # Resize maintaining aspect ratio but filling space (crop style)
                img_ratio = img.width / img.height
                target_ratio = target_width / screen_height
                
                if img_ratio > target_ratio:
                    # Image is wider, scale by height
                    new_height = screen_height
                    new_width = int(new_height * img_ratio)
                else:
                    # Image is taller, scale by width
                    new_width = target_width
                    new_height = int(new_width / img_ratio)
                    
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Center crop
                left = (new_width - target_width) / 2
                top = (new_height - screen_height) / 2
                right = (new_width + target_width) / 2
                bottom = (new_height + screen_height) / 2
                img = img.crop((left, top, right, bottom))
                
                self.bg_image = ImageTk.PhotoImage(img)
                tk.Label(parent, image=self.bg_image, bg="#f1f5f9").place(x=0, y=0, relwidth=1, relheight=1)
                
            else:
                # Gradient Fallback
                tk.Label(parent, text="NovaFlow", font=("Segoe UI", 40, "bold"), 
                        fg="#cbd5e1", bg="#f8fafc").place(relx=0.5, rely=0.5, anchor='center')
                
        except Exception as e:
            print(f"Image load error: {e}")
            tk.Label(parent, bg="#3b82f6").place(relx=0, rely=0, relwidth=1, relheight=1)

    def toggle_password(self):
        if self.show_pass_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="•")
    
    def login_action(self):
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password")
            return
        
        try:
            from services.auth_service import get_auth_service
            auth = get_auth_service()
            user, error = auth.authenticate(email, password)
            
            if user:
                self.on_login_success(user)
            else:
                messagebox.showerror("Login Failed", error)
                
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")

# For testing
if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root, lambda u: print(f"Login: {u}"))
    root.mainloop()