# Internal Complaint Portal - Learning Notes

## Day 1

---

# Git

| Command | Purpose | Where We'll Use It |
|---------|----------|--------------------|
| `git init` | Initializes a new Git repository. | Only once, when starting a new project. |
| `git add .` | Stages all modified files. | Before every commit. |
| `git commit -m "message"` | Saves a snapshot of your project. | After completing every feature or bug fix. |

---

# Virtual Environment

| Command | Purpose | Where We'll Use It |
|---------|----------|--------------------|
| `python -m venv venv` | Creates an isolated Python environment. | Only once during project setup. |
| `venv\Scripts\activate` | Activates the virtual environment. | Every time you start working on the backend. |

---

# Package Management

| Command | Purpose | Where We'll Use It |
|---------|----------|--------------------|
| `pip install <package>` | Installs a Python package. | Whenever a new dependency is needed. |
| `pip freeze > requirements.txt` | Saves all installed packages with versions. | After installing or updating project dependencies. |

---

# Flask

| Command | Purpose | Where We'll Use It |
|---------|----------|--------------------|
| `python app.py` | Starts the Flask development server. | Every time you want to test the backend locally. |

---

# Flask-Migrate

| Command | Purpose | Where We'll Use It |
|---------|----------|--------------------|
| `flask --app app db init` | Initializes Alembic and creates the `migrations/` folder. | Only once when migration support is first added. |
| `flask --app app db migrate -m "message"` | Generates a migration file by comparing models with the current database schema. | Every time you create or modify a model (add/remove columns, tables, relationships, etc.). |
| `flask --app app db upgrade` | Applies pending migrations to the PostgreSQL database. | Immediately after creating a migration so the database matches your models. |
| `flask --app app db downgrade` | Reverts the last applied migration. | When you need to undo an incorrect schema change during development. |

---

# Database

| Term | Meaning | Where We'll Use It |
|------|---------|--------------------|
| ORM | Maps Python classes to database tables. | Throughout the backend instead of writing raw SQL for CRUD operations. |
| SQLAlchemy | Flask's ORM library. | Used in every model and database query. |
| Migration | Version-controlled database schema changes. | Whenever the database structure changes. |
| Alembic | Migration engine used by Flask-Migrate. | Automatically runs behind the scenes when using migration commands. |

---

# Development Workflow

```
Create/Modify Model
        ↓
flask --app app db migrate -m "description"
        ↓
Migration File Generated
        ↓
flask --app app db upgrade
        ↓
Database Updated
```

### Rule to Remember

> Changing a Python model **does not** change the database.

The database is updated **only after** running:

```bash
flask --app app db upgrade
```