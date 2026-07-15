# Technical Code Explanation & Catalog
# Topic: Internal Complaint Portal (ICP) - Folder structure, Functions, and Packages

This document serves as a complete code manual. It lists every folder, file, function, and package utilized in the Internal Complaint Portal (ICP), explaining their roles and operations.

---

## 1. Backend Python Packages (`requirements.txt`)

These libraries are installed in the backend Python virtual environment:

| Package Name | Purpose / Why it is used |
| :--- | :--- |
| **`Flask`** | The core micro-framework used to construct the REST API and handle HTTP routing. |
| **`Flask-SQLAlchemy`** | Integrates SQLAlchemy with Flask, allowing us to write Python classes (models) that map to database tables. |
| **`Flask-Migrate`** | Handles SQL database migrations (updates tables automatically without losing existing database data). |
| **`Flask-CORS`** | Configures Cross-Origin Resource Sharing (CORS) headers, permitting your frontend (Port 8000) to communicate with your backend (Port 5000). |
| **`Flask-JWT-Extended`** | Manages JSON Web Tokens (JWT)—generates tokens, validates signatures, and checks token expiration. |
| **`psycopg2-binary`** | The PostgreSQL database adapter for Python, enabling Flask to talk directly to your PostgreSQL database. |
| **`bcrypt`** | A cryptographic hashing library used to secure user passwords with high-entropy salt factors. |

---

## 2. Frontend Libraries (CDNs in HTML)

These resources are loaded dynamically from Content Delivery Networks:

| Library | Purpose / Why it is used |
| :--- | :--- |
| **Bootstrap 5 (CSS & JS Bundle)** | Provides the pre-styled components (sidebar layout, tables, modals, input groups, buttons) for a modern, responsive layout. |
| **Bootstrap Icons** | Used for all interface icons (notification bell, edit pencil, delete trash, search magnifying glass, lock symbol). |
| **Outfit Font (Google Fonts)** | Added custom typography to override standard browser fonts, creating a premium interface. |

---

## 3. Directory Structure Catalog

```text
ICP/
├── backend/                  # Flask REST API Backend
│   ├── app.py                # Server entry point and configuration setup
│   ├── extensions.py         # SQLAlchemy & JWT initializations
│   ├── config.py             # Database and token lifespan variables
│   ├── seed.py               # Database seeder and reseter
│   ├── models/               # SQLAlchemy Database Schemas
│   │   ├── user.py           # User table with automatic EMP ID generation
│   │   ├── department.py     # Departments master data table
│   │   ├── category.py       # Categories master data table
│   │   └── complaint.py      # Tickets, Comments, Attachments, Logs, Notifications schemas
│   └── routes/               # Controllers (Blueprints)
│       ├── auth_routes.py    # Authentication, registration, user CRUD, self-profile
│       ├── admin_routes.py   # Admin-only category & department CRUD
│       ├── complaint_routes.py# Core ticket workflow operations, comments, attachments
│       ├── manager_routes.py # Technician assignment listings and triggers
│       ├── technician_routes.py# Tasks acceptance and resolutions
│       ├── notification_routes.py# User unread notifications queues
│       └── report_routes.py  # Analytical aggregation utilities
│
├── frontend/                 # Client UI (Single Page Application)
│   ├── index.html            # Landing page redirect gatekeeper
│   ├── login.html            # Login interface and inline AJAX controller
│   ├── dashboard.html        # Centralized user interface panels and modals
│   ├── css/style.css         # Styling overrides (responsive sidebar stacking)
│   └── js/
│       ├── auth.js           # Decodes JWT tokens (with base64 padding) & controls route guards
│       └── dashboard.js      # Consolidates all AJAX requests, table loads, and tab switches
```

---

## 4. Detailed Function Catalog

### Backend Configuration & Setup
#### `backend/app.py`
*   `create_app()`: Initializes the main Flask application context, registers CORS allowances, handles database and JWT bindings, and loads all Blueprints.

#### `backend/seed.py`
*   `seed_database()`: Clears the PostgreSQL database (using child-first dependency sequence to bypass foreign key constraint failures) and seeds default departments, categories, and the primary administrator.
*   `create_default_user()`: Encrypts passwords using Bcrypt and inserts user accounts.

### Authentication & Authorization Blueprint (`routes/auth_routes.py`)
*   `login()`: Validates password hashes against user emails, generating and returning JWT tokens.
*   `register()`: Admin/Manager-only endpoint to register users. Auto-generates unique `EMPxxx` codes.
*   `get_users()`: Returns a list of all user records.
*   `update_user()`: Modifies role, department, and active/inactive status.
*   `delete_user()`: Safely deletes user accounts if they have no active complaints linked.
*   `update_profile()`: Allows any logged-in user to update their display name or change their password (requires current password validation).

### Admin Controls Blueprint (`routes/admin_routes.py`)
*   `get_departments()` / `create_department()` / `update_department()` / `delete_department()`: Standard CRUD operations for departments. Prevents deletion if active users or categories are linked.
*   `get_categories()` / `create_category()` / `update_category()` / `delete_category()`: Standard CRUD operations for categories. Prevents deletion if active complaints exist under the category.

### Ticket Workflows Blueprint (`routes/complaint_routes.py`)
*   `create_complaint()`: Creates a new ticket, uploads initial attachments, routes it to the target department, logs history, and alerts administrators.
*   `get_complaints()`: Returns lists of complaints. Filters based on roles (Employees see own tickets, Techs/Managers see department-wide tickets, Admins see all).
*   `get_complaint_details()`: Returns a single ticket along with its comments and attachments.
*   `update_complaint_status()`: Coordinates status transitions (`New` -> `Assigned` -> `Accepted` -> `In Progress` -> `Resolved` -> `Closed`).
*   `add_comment()`: Registers comment annotations on a ticket.
*   `upload_attachment()`: Appends new files to an existing ticket.

### Assignment Blueprint (`routes/manager_routes.py`)
*   `get_department_technicians()`: Returns list of technicians. For administrators, resolves department context dynamically via complaint parameters.
*   `assign_technician()`: Initial assignment of a technician to a new ticket.
*   `reassign_technician()`: Reassigns a technician, recording the change in the history log.

### Frontend Javascript Function Catalog
#### `frontend/js/auth.js`
*   `parseJwt(token)`: Decodes the payload portion of a JWT token, calculating and appending missing trailing base64 padding (`=`) to prevent decryption crashes in the browser.
*   `getAuthUser()`: Verifies token presence and checks for expiration.
*   `logoutUser()`: Clears local storage and redirects to the login screen.
*   `requireAuth()` / `requireGuest()`: Direct route guards protecting page layouts.

#### `frontend/js/dashboard.js`
*   `switchTab(tabId)`: Coordinates Single-Page App tab navigation, hiding inactive panes and triggering data loading functions.
*   `apiFetch(endpoint, options)`: Wrapper for API requests. Appends JWT headers and handles session timeouts.
*   `loadHomeStats()` / `loadReportsAndCharts()`: Loads statistics and renders CSS-based progress-bar charts.
*   `loadComplaintsList()`: Queries, searches, and filters the complaints tables.
*   `openComplaintDetails(id)`: Fetches details and updates the interactive chat and timeline views.
*   `submitProfileUpdate()`: Submits password and display name updates.
*   `loadAdminSettings()` / `loadDepartmentsTable()` / `loadCategoriesTable()`: Populates tables for department and category CRUD.
*   `showToastNotification(msg, type)`: Slides a dynamic notification toast into the bottom-right corner.
*   `clearAllNotifications(e)`: Clears the notification dropdown list.
