# ✨ NovaFlow Enterprise System


**NovaFlow** is a modern, robust desktop application designed to streamline enterprise resource management. From employee tracking to inventory control, NovaFlow provides a unified interface for managing your business operations.

---

## Key Features

### 🔐 Secure Authentication
- **Modern Login UI**: Split-screen design with a dark aesthetic.
- **Secure Hashing**: Passwords are salted and hashed for maximum security.
- **Password Recovery**: Integrated "Forgot Password" flow with email verification (simulation).

### 👥 Human Resources
- **Employee Management**: detailed profiles including specialized fields for Salesmen, HODs, and Supervisors.
- **Compensation Tracking**: Dynamic salary fields based on employee roles (Hourly vs Fixed vs Commission).
- **Department Hierarchy**: Manage departments, locations, and Head of Department (HOD) assignments.

### 📦 Inventory & Logistics
- **Multi-Warehouse Support**: Create and manage warehouses with assigned supervisors.
- **Product Catalog**: Global product registry with detailed specifications.
- **Stock Management**: Track stock levels across different warehouse locations.

### 📊 Project & Work Logs
- **Project Tracking**: Manage generic projects with budgets, timelines, and locations.
- **Work Logs**: Employees can submit daily work hours logged against specific projects.

---

## UI/UX Design
The application features a custom **Dark Navy (#0f172a)** theme, providing a professional and consistent user experience.
- **Consistent Headers**: All dialogs share a unified branding style.
- **Validation**: Real-time form validation with clear error messages.
- **Responsive Forms**: Scrollable inputs for data-heavy entry screens.

---

## Technology Stack
- **Language**: Python 3.x
- **GUI Framework**: Tkinter (Native)
- **Database**: MySQL (via `pymysql`)
- **Assets**: PIL (Pillow) for image rendering

---

## Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/wajidcodes/NovaFlow-Company-Management-System-Python-MySQL-.git
   cd NovaFlow-Company-Management-System-Python-MySQL-
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Database Configuration**
    - Ensure your MySQL server is running.
    - Import the database schema (provided separately).
    - Update `config/database.py` with your credentials.

4.  **Run the Application**
    ```bash
    python main.py
    ```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

<p align="center">
  Built with ❤️ by the NovaFlow Team
</p>
