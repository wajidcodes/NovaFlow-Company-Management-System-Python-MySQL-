# System Requirements

To run the **NovaFlow Enterprise System**, ensure your environment meets the following specifications.

## 🐍 Python Version
- **Python 3.8** or higher is required.

## 📦 Key Dependencies
The following Python packages are required. You can install them using `pip`.

| Package | Version | Usage |
| :--- | :--- | :--- |
| `pymysql` | Latest | Connects to the MySQL database. |
| `Pillow` | Latest | Handles image processing for UI assets. |
| `tkinter` | Built-in | The Standard Python GUI library (usually comes with Python). |
| `python-dotenv` | Latest | Loads environment variables from the `.env` file. |

## 🛠️ Installation
Run the following command in your terminal to install all dependencies:

```bash
pip install -r requirements.txt
```

## 🗄️ Database
- **MySQL Server** (8.0 or higher recommended)
- A running instance of the database using the provided `schema.sql` (if available) or existing connection parameters.
