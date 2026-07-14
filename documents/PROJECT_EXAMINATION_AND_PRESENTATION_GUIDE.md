# Internal Complaint Portal (ICP) - Project Examination & Presentation Guide

This guide is designed to prepare you for **project reviews, examinations, and presentations**. It lists the most common technical questions an evaluator, professor, or interviewer will ask about this codebase, along with clear, student-friendly answers and the underlying code references.

---

## Part 1: Core Architecture & Design Patterns

### Q1: What is the overall architecture of this application?
*   **The Answer**: This project uses a **multi-layered, decoupled client-server architecture** (also known as a headless or API-first architecture).
    *   **Backend (Flask)**: Acts as a pure REST API. It connects to the database, enforces security, and returns data in JSON format. It does not render or serve HTML.
    *   **Frontend (Bootstrap 5 & Vanilla JavaScript)**: Consists of static files (`.html`, `.css`, `.js`) that run entirely in the browser. It queries the backend via asynchronous `fetch()` API calls and updates the page dynamically.
*   **Why this is good**: It decouples the user interface from the server logic. If we want to build a mobile app in the future, we can reuse the exact same backend API without changing a single line of Python code.

### Q2: How is the backend code structured? Why not put everything in one file?
*   **The Answer**: The backend is organized into three distinct layers to follow the **Separation of Concerns (SoC)** design principle:
    1.  **Models Layer (`backend/models/`)**: Defines the database schema and structures (e.g., [user.py](file:///D:/Projects/ICP/backend/models/user.py)). It only knows about database columns and data types.
    2.  **Routes Layer (`backend/routes/`)**: Acts as the traffic controller (e.g., [complaint_routes.py](file:///D:/Projects/ICP/backend/routes/complaint_routes.py)). It receives HTTP requests, parses the JSON payload, checks authorization, and sends back HTTP responses.
    3.  **Services Layer (`backend/services/`)**: Contains the actual business logic (e.g., [complaint_service.py](file:///D:/Projects/ICP/backend/services/complaint_service.py)). It handles database transactions, computes metrics, and generates notifications.
*   **Why this is good**: It makes the code modular, maintainable, and testable. If we need to change how a complaint is processed, we only modify the Service layer; the Routes and Models layers remain untouched.

---

## Part 2: Database & SQLAlchemy (ORM)

### Q3: What is an ORM? Why did we use SQLAlchemy instead of raw SQL queries?
*   **The Answer**: **ORM** stands for **Object-Relational Mapping**. It is a programming technique that allows us to interact with a relational database (like PostgreSQL) using object-oriented code (Python classes and objects) instead of writing raw SQL strings (like `SELECT * FROM users`).
*   **Why this is good**:
    1.  **Readability**: Python code like `User.query.all()` is easier to read and maintain than raw SQL queries.
    2.  **Security**: SQLAlchemy automatically uses parameterized queries, which protects the application from **SQL Injection attacks**.
    3.  **Database Agnostic**: If we want to switch our database from PostgreSQL to MySQL or SQLite, we only change the connection string configuration. SQLAlchemy translates our Python operations into the correct SQL dialect automatically.

### Q4: Explain the database relationships in this project.
*   **The Answer**:
    *   **One-to-Many (Category & Complaint)**: A `Category` (e.g. "Printer") has many `Complaints`. Inside the `Category` model, this is defined using `db.relationship('Complaint', backref='category')`. This adds a virtual `.category` attribute to each complaint object, allowing us to read the category details directly (e.g. `complaint.category.name`).
    *   **Many-to-One (Complaint & User)**: A `Complaint` belongs to an employee (who raised it) and a technician (who resolves it). These are linked using foreign keys pointing to the same `users.id` primary key. In the `User` model, we specify separate relationships using `foreign_keys` arguments:
        ```python
        raised_complaints = db.relationship("Complaint", foreign_keys="[Complaint.employee_id]", backref="employee")
        assigned_complaints = db.relationship("Complaint", foreign_keys="[Complaint.technician_id]", backref="technician")
        ```

### Q5: What does `cascade="all, delete-orphan"` mean in our models?
*   **The Answer**: This configures database referential integrity. If a parent record (like a `Complaint`) is deleted from the database, SQLAlchemy will automatically delete all dependent child records (such as its `Comments` or `Attachments`). This prevents **orphan records** from cluttering the database and ensures we do not violate foreign key constraints.

---

## Part 3: Security & Authentication

### Q6: How does JWT (JSON Web Token) authentication work in this application?
*   **The Answer**: We use **token-based authentication**:
    1.  The user enters their email and password on [login.html](file:///D:/Projects/ICP/frontend/login.html).
    2.  The backend verifies the credentials. If correct, it generates a signed JWT access token containing secure claims (the user's ID, name, and role) and sends it back to the client.
    3.  The frontend stores this token in the browser's `localStorage` (via [auth.js](file:///D:/Projects/ICP/frontend/js/auth.js)).
    4.  For every subsequent request to secure pages (like fetching complaints), the frontend attaches the token in the HTTP header: `Authorization: Bearer <token>`.
    5.  The backend decodes and verifies the signature of the token. If valid, it allows access.
*   **Why this is good**: It is **stateless**. The server does not need to store session IDs in memory or perform database lookups to verify who the user is on every single request. All information is self-contained within the signed token.

### Q7: Why do we use Bcrypt for passwords instead of MD5 or SHA256?
*   **The Answer**: MD5 and SHA256 are fast cryptographic hashes. However, because they are fast, they are highly vulnerable to **brute-force attacks** and **rainbow table lookups** if the database is leaked. Bcrypt is a **key-derivation hashing function** designed to be slow. It incorporates a random "Salt" and has a configurable work factor, making brute-force attacks computationally infeasible.

---

## Part 4: REST API & CORS

### Q8: What is CORS? Why did we get CORS errors, and how did we resolve them?
*   **The Answer**: **CORS** stands for **Cross-Origin Resource Sharing**. It is a browser security mechanism (Same-Origin Policy) that blocks frontend scripts on one origin (e.g. `http://localhost:8000`) from reading data from a server on a different origin (e.g. `http://127.0.0.1:5000`) unless the server explicitly sends headers allowing it.
*   **How we resolved it**:
    1.  **Backend**: We installed `Flask-CORS` and initialized it with `CORS(app)` in [app.py](file:///D:/Projects/ICP/backend/app.py). This tells the backend to send the response header `Access-Control-Allow-Origin: *`.
    2.  **Windows IPv4/IPv6 Mismatch**: On Windows, `localhost` resolves to the IPv6 address `[::1]`. If Flask runs on IPv4 `127.0.0.1` and the client requests `localhost`, the browser sees a network connection refusal and reports it as a CORS block. We fixed this by changing all frontend endpoints strictly to `127.0.0.1`.

### Q9: What is a preflight request (OPTIONS)?
*   **The Answer**: When the frontend makes a request containing custom headers (like `Authorization: Bearer <token>`) or content types other than simple text, the browser automatically sends a preliminary HTTP request using the `OPTIONS` method before the actual request. This is called a **preflight request**. It checks with the server if the cross-origin request is safe to send.

---

## Part 5: Frontend Single Page Application (SPA)

### Q10: How does tab switching work without using React or Vue?
*   **The Answer**: We implemented a lightweight, pure JavaScript single-page router in [dashboard.js](file:///D:/Projects/ICP/frontend/js/dashboard.js) using the `switchTab(tabId)` function:
    1.  We listen for click events on elements containing the `data-tab` attribute.
    2.  When clicked, the function selects all tab pane elements (`.tab-pane`) and adds Bootstrap's `.d-none` (display: none) CSS class to hide them.
    3.  It then selects the target panel by ID (e.g. `document.getElementById(tabId)`) and removes `.d-none` to display it.
    4.  Finally, it triggers specific data loading functions (like `loadComplaintsList()`) to populate the newly displayed screen.

### Q11: Explain how the dashboard statistics and progress charts are rendered.
*   **The Answer**: Instead of relying on large external chart libraries, we built **CSS-based charts** directly inside [dashboard.js](file:///D:/Projects/ICP/frontend/js/dashboard.js#L688-L745):
    1.  We fetch counts from the server (e.g., ticket distributions per department).
    2.  We find the maximum count among all departments.
    3.  We calculate the relative percentage width for each department: `const pct = Math.round((count / max) * 100)`.
    4.  We render standard Bootstrap progress bars and set their inline width dynamically using JavaScript: `style="width: ${pct}%"`.
*   **Why this is good**: It is extremely lightweight, uses native CSS rendering, and is highly explainable compared to complex canvas-based charting scripts.

---

## Part 6: Troubleshooting & Edge Cases

### Q12: Why did we need to add base64 padding to the JWT decoder in Javascript?
*   **The Answer**: JWT payload segments are encoded in **base64url** format, which omits trailing padding signs (`=`) to save URL space. However, standard browser JavaScript `window.atob()` requires base64 strings to have a length that is a multiple of 4. If we try to decode a non-padded string, the browser crashes with a `DOMException` error. In [auth.js](file:///D:/Projects/ICP/frontend/js/auth.js#L21-L22), we calculate how many characters are missing and append them before decoding:
    ```javascript
    const padding = '='.repeat((4 - (base64.length % 4)) % 4);
    const base64WithPadding = base64 + padding;
    const decoded = window.atob(base64WithPadding);
    ```

### Q13: Why did we experience an infinite redirect loop when double-clicking HTML files?
*   **The Answer**: Double-clicking HTML files opens them under the `file://` protocol. For security, modern browsers isolate the `localStorage` context of every single file running under the `file://` protocol. Therefore, `login.html` and `dashboard.html` could not share the JWT access token. On login, the token was stored under `login.html`. Upon redirecting to `dashboard.html`, the storage was empty, which triggered a redirect back to `login.html`. Hosting the pages on a local server (`http://localhost:8000`) assigns them to the same origin, resolving the storage isolation.
