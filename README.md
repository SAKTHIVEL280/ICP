# Internal Complaint Portal (ICP) - Full Setup Guide

The **Internal Complaint Portal (ICP)** is a secure, decoupled web application that allows employees to submit internal issues (IT, Facilities, HR, Maintenance, and Workplace Safety) which are routed automatically to responsible departments for technicians to accept, track, and resolve.

---

## 1. Project Directory Structure

```text
ICP/
├── backend/                  # Flask REST API Backend
│   ├── app.py                # Server entry point
│   ├── requirements.txt      # Python dependencies
│   ├── seed.py               # Database initialization seeder
│   └── models/, routes/, services/
│
├── frontend/                 # Client UI (Bootstrap 5, Vanilla JS)
│   ├── index.html            # Landing page redirect gatekeeper
│   ├── login.html            # Sign-in page
│   ├── dashboard.html        # Single-page client dashboard
│   ├── css/style.css         # Styling overrides
│   └── js/auth.js, dashboard.js
│
└── documents/                # Walkthroughs, Q&A logs, and Design sheets
```

---

## 2. How to Run the Backend (Port 5000)

### Prerequisites:
Make sure you have **PostgreSQL** installed and running on your system, and a database named `internal_complaint_portal` created.

### Steps:
1.  Open a terminal and navigate to the backend folder:
    ```bash
    cd D:\Projects\ICP\backend
    ```
2.  Activate the virtual environment:
    *   **PowerShell**:
        ```powershell
        venv\Scripts\Activate.ps1
        ```
    *   **Git Bash / Linux / macOS**:
        ```bash
        source venv/Scripts/activate
        ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Apply database migrations to configure PostgreSQL tables:
    ```bash
    flask --app app db upgrade
    ```
5.  Start the Flask server:
    ```bash
    python app.py
    ```
    The backend will run on: **`http://127.0.0.1:5000`**

---

## 3. How to Run the Frontend (Port 8000)

> [!IMPORTANT]
> **Do not open `login.html` by double-clicking it on your disk.** Modern browser security (Same-Origin Policy) isolates storage for local files (`file://`), preventing `login.html` and `dashboard.html` from sharing access tokens. You must run a local web server to host them on the same origin.

### Steps:
1.  Open a **second** terminal window.
2.  Navigate to the frontend folder:
    ```bash
    cd D:\Projects\ICP\frontend
    ```
3.  Start a lightweight Python web server:
    ```bash
    python -m http.server 8000
    ```
4.  Open your browser and navigate to:
    **`http://localhost:8000/login.html`** (or `http://127.0.0.1:8000/login.html`)

---

## 4. Sandbox Test Credentials

Use the default Administrator account to access the portal. You can then use the **User Management** tab to register other roles, the **System Config** tab to configure departments/categories, or click **Edit Profile** to update your account settings:

| Role | User Name | Login Email | Password | Employee ID |
| :--- | :--- | :--- | :--- | :--- |
| **Administrator** | System Administrator | `admin@company.com` | `Admin@123` | `EMP001` |

---

## 5. Help and Explanations
For a complete line-by-line explanation of the code, imports, and how to answer presentation questions:
*   Read **[LEARNING GUIDE.md](file:///D:/Projects/ICP/documents/LEARNING%20GUIDE.md)** for file and code structures.
*   Read **[PROJECT_EXAMINATION_AND_PRESENTATION_GUIDE.md](file:///D:/Projects/ICP/documents/PROJECT_EXAMINATION_AND_PRESENTATION_GUIDE.md)** for examination Q&A logs.
