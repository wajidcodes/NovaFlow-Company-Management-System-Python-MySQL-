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

## Project Structure

```text
.
├── main.py                 # Application entry point
├── Database/               # schema.sql, Schema_legacy.sql, add_project.sql
├── config/                 # Database configuration (database.py)
├── dialogs/                # UI dialogs
├── models/                 # Data models
├── services/               # Business logic
├── utils/                  # Helper utilities
├── views/                  # UI views
├── Users/                  # User-related modules
├── Style/                  # UI styling
├── Images/                 # Image assets
├── requirements.txt        # Python dependencies
├── REQUIREMENTS.md         # System requirements
├── .env.example            # Example environment variables
└── LICENSE.md              # MIT License
```

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

3.  **Set up MySQL (required — the app cannot run without it)**
    - Install **MySQL 8.0 or higher** and make sure the server is running.
    - Import the schema. This creates the `company_management` database, 18 tables, and seed data (94 people, plus departments, projects, products and orders):
      ```bash
      mysql -u root -p < Database/schema.sql
      ```
    - Copy `.env.example` to `.env` and fill in your MySQL credentials:
      ```bash
      cp .env.example .env
      ```
      The app reads `DB_HOST`, `DB_USER`, `DB_PASSWORD` and `DB_NAME` from `.env`, so there is no need to edit `config/database.py`.
    - **Why this step is required:** the login screen checks your email and password against the database on the first attempt (`services/auth_service.py` calls `get_db_connection()`), so without a running MySQL server, the imported schema and a filled `.env`, you cannot get past login. There is no offline or demo mode.
    - **Demo login (seed data):** after importing the schema, sign in with `wajid.ali@company.com` / `password123`. This is a seeded demo account from `Database/schema.sql` — change its password before any real use.

4.  **Run the Application**
    ```bash
    python main.py
    ```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/wajidcodes">Wajid Ali</a> · <a href="https://wajidali-portfolio.vercel.app">Portfolio</a>
</p>
