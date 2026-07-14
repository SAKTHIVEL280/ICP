# Internal Complaint Portal (ICP) - Comprehensive Student Learning Guide

Welcome to the learning guide for the **Internal Complaint Portal (ICP)**. This document acts as a walkthrough of the entire project codebase. It explains the purpose of every file, what the imports do, and the step-by-step logic of key functions.

---

## 1. Project Directory Structure

```text
ICP/
│
├── documents/                      # Design specifications & system architecture
│   ├── BACKEND DESIGN.md
│   ├── DATABASE DESIGN.md
│   ├── FRONTEND DESIGN.md
│   ├── INTERNAL COMPLAINT PORTAL.md
│   ├── LEARNING GUIDE.md           # This file! Walkthrough of all code files & details.
│   └── PROJECT_EXAMINATION_AND_PRESENTATION_GUIDE.md # Review Q&A guide for presentations.
│
├── backend/                        # Flask Backend Application
│   ├── app.py                      # Flask entry point and Blueprint registration
│   ├── config.py                   # App configurations (database URLs, JWT keys)
│   ├── extensions.py               # Shared SQLAlchemy, Migrate, & JWT instances
│   ├── requirements.txt            # Python package dependencies
│   ├── seed.py                     # Initial database seeder script
│   ├── models/                     # SQLAlchemy Database Models (schema)
│   │   ├── activity_log.py
│   │   ├── attachment.py
│   │   ├── category.py
│   │   ├── comment.py
│   │   ├── complaint_history.py
│   │   ├── complaint.py
│   │   ├── department.py
│   │   ├── notification.py
│   │   └── user.py
│   ├── routes/                     # Blueprint API Endpoints (receives requests)
│   │   ├── auth_routes.py
│   │   ├── complaint_routes.py
│   │   ├── manager_routes.py
│   │   ├── notification_routes.py
│   │   ├── report_routes.py
│   │   └── test_routes.py
│   └── services/                   # Business Logic & Database operations
│       ├── auth_service.py
│       ├── complaint_service.py
│       ├── notification_service.py
│       └── report_service.py
│
└── frontend/                       # Client Web Interface (Bootstrap 5, JS)
    ├── index.html                  # Landing page (checks auth state & redirects)
    ├── login.html                  # Simple Bootstrap sign-in page
    ├── dashboard.html              # Core single-page dashboard shell
    ├── css/                        # CSS stylesheets
    │   └── style.css               /* Simple overrides (sidebar width, timeline lines) */
    └── js/                         # Frontend JS modules
        ├── auth.js                 /* Session helper: decodes JWT tokens and controls page guards */
        └── dashboard.js            /* Consolidated UI script: loads lists, panels, and API forms */
```

---

## 2. Backend Architecture Walkthrough

### A. Setup Files

#### 1. `backend/extensions.py`
*   **What it does**: This file initializes database and migration instances so they can be imported and shared across multiple files without causing circular dependencies.
*   **Key Imports & Lines**:
    *   `db = SQLAlchemy()`: Creates the database coordinator object.
    *   `migrate = Migrate()`: Creates the migrations controller.
    *   `jwt = JWTManager()`: Creates the JWT token coordinator.

#### 2. `backend/app.py`
*   **What it does**: Flask entrypoint. It configures the app, enables CORS so the browser can query it, registers Blueprint routes, and runs the dev server.
*   **Key Imports & Lines**:
    *   `from flask_cors import CORS`: Enables Cross-Origin Resource Sharing.
    *   `app.register_blueprint(...)`: Sets up URL prefixes (e.g. `/api/auth`, `/api/complaints`).

---

### B. Database Models (`backend/models/`)

These files define the schemas of our tables in PostgreSQL.

1.  **[user.py](file:///D:/Projects/ICP/backend/models/user.py)**: Represents the `users` table, which holds names, hashed passwords, roles, and department IDs.
2.  **[category.py](file:///D:/Projects/ICP/backend/models/category.py)**: Represents category options (like Printer, Laptop) and connects them to a responsible department.
3.  **[complaint.py](file:///D:/Projects/ICP/backend/models/complaint.py)**: Represents tickets containing details, status, priority, location, and uploader IDs.
4.  **[comment.py](file:///D:/Projects/ICP/backend/models/comment.py)**: Represents discussion comments on tickets.
5.  **[attachment.py](file:///D:/Projects/ICP/backend/models/attachment.py)**: Logs filenames and folder paths of uploaded files.

---

### C. Services & Business Logic (`backend/services/`)

1.  **[complaint_service.py](file:///D:/Projects/ICP/backend/services/complaint_service.py)**:
    *   `create_complaint(data, employee_id)`: Saves tickets in database. Automatically maps the correct department based on the selected category (Fulfills the auto-routing design requirement!). Also creates starting logs and alerts department managers.
    *   `verify_and_close_complaint(complaint_id, action, employee_id)`: Allows employees to close resolved tickets or reopen them (shifting status back to In Progress).
2.  **[notification_service.py](file:///D:/Projects/ICP/backend/services/notification_service.py)**: Manages alerts and marks them as read.
3.  **[report_service.py](file:///D:/Projects/ICP/backend/services/report_service.py)**: Computes counts grouped by priority, category, or department for manager graphs.

---

## 3. Frontend Architecture Walkthrough

The frontend has been redesigned to use **Bootstrap 5** and consolidated into just **two JavaScript files** to make it extremely simple, lightweight, and easy to explain.

### A. Landing page & Login Redirects

#### 1. [index.html](file:///D:/Projects/ICP/frontend/index.html)
*   **What it does**: Checks if an access token exists in browser localStorage on load. If the user is authenticated, it opens `dashboard.html`. Otherwise, it redirects to `login.html`.

#### 2. [login.html](file:///D:/Projects/ICP/frontend/login.html)
*   **What it does**: Displays a centered sign-in card.
*   **Key JavaScript Lines**:
    *   `requireGuest()`: Runs on load. If a session exists, it skips login and sends the user to `dashboard.html`.
    *   `fetch("http://localhost:5000/api/auth/login", { ... })`: On form submit, sends user email and password to Flask.
    *   `localStorage.setItem("access_token", data.access_token)`: Stores the returned authentication token securely in browser memory.

---

### B. Session Management: [auth.js](file:///D:/Projects/ICP/frontend/js/auth.js)

*   **Key Function**: `parseJwt(token)`
    *   *What it does*: Decodes a JSON Web Token (JWT) on the client side.
    *   *How it works*: A JWT is split by dots (`.`). The payload is base64url encoded at index 1. We replace URL characters (`-` and `_`) with standard base64 characters (`+` and `/`). 
    *   *Critical Student Note (Padding)*: Browser `window.atob()` will fail and throw an error if the base64 string length is not a multiple of 4. We calculate missing padding characters with `const padding = '='.repeat(...)` and append them to ensure decoding succeeds on all web browsers.
*   **Key Function**: `getAuthUser()`
    *   *What it does*: Verifies if a token exists, decodes it, checks if the expiration timestamp (`payload.exp`) is greater than current time, and returns the claims `{ id, name, role }`.
*   **Key Guards**:
    *   `requireAuth()`: Kicks guests to `login.html` (used on `dashboard.html`).
    *   `requireGuest()`: Kicks logged-in users to `dashboard.html` (used on `login.html`).

---

### C. UI Rendering & API Syncing: [dashboard.js](file:///D:/Projects/ICP/frontend/js/dashboard.js)

Consolidates all page logic into a single, clean file.

*   **Key Function**: `apiFetch(endpoint, options)`
    *   *What it does*: A wrapper for standard JavaScript `fetch()`. It automatically inserts the header `Authorization: Bearer <token>` if a token exists. If the server rejects the request with HTTP `401 Unauthorized` (token expired/invalid), it clears the token and redirects the browser to the login page.
*   **Key Function**: `switchTab(tabId)`
    *   *What it does*: Manages view switching for our single-page application dashboard.
    *   *How it works*: It hides all panel templates by adding Bootstrap's `.d-none` (display: none) class, and reveals the selected tab pane by removing it. It then triggers specific loaders (like pulling stats or categories list).
*   **Key Function**: `setupSidebarMenus()`
    *   *What it does*: Implements role-based visibility in the sidebar. It reads the user's role and displays buttons matching their profile.
*   **Key Function**: `loadComplaintsList()`
    *   *What it does*: Queries the server for complaint records. It chooses different API endpoints depending on user roles (Manager, Technician, Employee) and renders rows into the table body.
*   **Key Function**: `loadReportsAndCharts()`
    *   *What it does*: Renders department and priority counts.
    *   *CSS Charts*: Instead of drawing complex canvases with external chart libraries, it calculates widths using percentages (`Math.round((d.count / max) * 100)`) and sets the inline CSS width of Bootstrap's progress bars (`style="width: ${pct}%"`). This creates premium-looking responsive charts using clean, explainable HTML and CSS!

---

## 4. Hierarchical User Creation (User Management Console)

The user registration endpoint `POST /api/auth/register` is secured and restricted. The creation of new user accounts follows an administrative hierarchy:

1.  **Access Rules**:
    *   **Administrator**: Full access. Can create any user role (Employee, Technician, Manager, Administrator) in any department.
    *   **Manager**: Department-restricted. Can register new users, but their department ID is locked to the manager's department, and they can only assign `Employee` or `Technician` roles (cannot create managers/admins).
    *   **Employee / Technician**: Access denied. Cannot register or view user listings.
2.  **Implementation Code**:
    *   **Backend ([auth_routes.py](file:///D:/Projects/ICP/backend/routes/auth_routes.py#L8-L47))**: The route checks token claims. If a manager submits, it overrides the `department_id` in the request body with the manager's own `department_id` and checks that the role is either `Employee` or `Technician`.
    *   **Frontend ([dashboard.js](file:///D:/Projects/ICP/frontend/js/dashboard.js#L868-L985))**: The `openCreateUserModal()` function detects the current user's role. For managers, it hides the department dropdown input (removing the `required` validation rule) and excludes Manager/Admin choices from the role selection list.

---

## 5. CORS and Loopback Troubleshooting (Windows IPv6 / IPv4 Mismatch)

When querying a backend running locally, you might encounter a "CORS error" that is actually a local loopback resolution failure.
*   **The Issue**: On Windows, `localhost` dynamically resolves to the IPv6 loopback address `[::1]`. When Flask starts, it binds strictly to the IPv4 address `127.0.0.1:5000`. When the browser makes a request to `localhost:5000`, the connection is refused. Browsers often report this network refusal as a generic CORS preflight failure.
*   **The Fix**: All frontend API calls are explicitly routed to `http://127.0.0.1:5000/api` (rather than `localhost:5000`). This aligns with Flask's active binding and bypasses loopback failures.

---

## 6. Sandbox Test Credentials

The database contains a single System Administrator account. All other accounts have been wiped so you can test user registration yourself:

| Role | User Name | Login Email | Password |
| :--- | :--- | :--- | :--- |
| **Administrator** | System Administrator | `admin@company.com` | `Admin@123` |

### To test the portal:
1.  Log in as the **System Administrator** (`admin@company.com` / `Admin@123`).
2.  Go to the **User Management** tab.
3.  Click **Create New User** to register:
    *   A Manager (e.g., Sarah Connor in IT Support).
    *   A Technician (e.g., Alice Smith in IT Support).
    *   An Employee (e.g., David Miller).
4.  Log out and log in under your new accounts to test the ticket workflow!
