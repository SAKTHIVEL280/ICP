# Internal Complaint Portal - Backend Design

## Overview

This document describes the backend architecture for the **Internal
Complaint Portal**. The backend follows a layered architecture using
**Flask**, **PostgreSQL**, and **JWT Authentication**.

------------------------------------------------------------------------

# Architecture

``` text
Client (HTML/CSS/JavaScript)
            │
            │ REST API
            ▼
+---------------------------+
|      Flask Backend        |
+---------------------------+
| Authentication Module     |
| Complaint Module          |
| User Module               |
| Department Module         |
| Category Module           |
| Assignment Module         |
| Comment Module            |
| Attachment Module         |
| Notification Module       |
| Report Module             |
| Admin Module              |
+---------------------------+
            │
            ▼
      PostgreSQL Database
```

------------------------------------------------------------------------

# Project Structure

``` text
backend/
│
├── app.py                      # Flask entry point and Blueprint registration
├── config.py                   # App configurations (database URLs, JWT keys)
├── extensions.py               # Shared SQLAlchemy, Migrate, & JWT instances
├── requirements.txt            # Python package dependencies
├── seed.py                     # Initial database seeder script
│
├── routes/                     # Blueprint API Endpoints
│   ├── auth_routes.py          # /api/auth/* endpoints (login, register, users listing)
│   ├── complaint_routes.py     # /api/complaints/* endpoints (standard CRUD, comments)
│   ├── manager_routes.py       # /api/manager/* endpoints (technician assignment)
│   ├── notification_routes.py  # /api/notifications/* endpoints (alerts list)
│   ├── report_routes.py        # /api/reports/* endpoints (summary counts, CSS charts)
│   └── test_routes.py          # Quick development diagnostic routes
│
├── services/                   # Business Logic & Database operations
│   ├── auth_service.py         # Login and password validation
│   ├── complaint_service.py    # Ticket lifecycle state changes & auto routing
│   ├── notification_service.py # Alert generation triggers
│   └── report_service.py       # Computes statistics counts
│
├── models/                     # SQLAlchemy Database Models (schema)
│   ├── user.py
│   ├── complaint.py
│   ├── department.py
│   ├── category.py
│   ├── comment.py
│   ├── attachment.py
│   ├── notification.py
│   ├── complaint_history.py
│   └── activity_log.py
│
├── middleware/                 # Helper middlewares
│   └── role_required.py        # Role-based access wrapper
│
└── uploads/                    # Local storage folder for uploaded file attachments
```

------------------------------------------------------------------------

# Layer Responsibilities

## Routes

-   Receive HTTP requests.
-   Validate incoming payloads (check for missing parameters).
-   Route traffic and invoke service layer handlers.
-   Return HTTP JSON responses.

## Services

-   Implement core business logic.
-   Coordinate database transaction operations.
-   Trigger notification creations and logs.

## Models

-   SQLAlchemy ORM models representing PostgreSQL tables.

------------------------------------------------------------------------

# Authentication Flow

``` text
Login
 ↓
Verify Credentials
 ↓
Generate JWT
 ↓
Return Token
 ↓
Client Sends Token
 ↓
Protected API Access
```

------------------------------------------------------------------------

# Role-Based Authorization

  Role            Permissions
  --------------- ------------------------------------------------------------
  Employee        Create/view own complaints, comment, verify completion
  Technician      Accept assignments, update status, upload evidence
  Manager         Assign/reassign technicians, monitor department complaints
  Administrator   Full system access

Example:

``` python
@jwt_required()
@role_required("Manager")
```

------------------------------------------------------------------------

# Complaint Workflow

``` text
Employee
   ↓
Create Complaint
   ↓
Auto Department Assignment
   ↓
Status = NEW
   ↓
Manager Assigns Technician
   ↓
Status = ASSIGNED
   ↓
Technician Accepts
   ↓
Status = ACCEPTED
   ↓
Work In Progress
   ↓
Status = IN_PROGRESS
   ↓
Resolved
   ↓
Employee Verification
   ↓
Closed
```

Every status change creates records in: - Complaint History - Activity
Log

------------------------------------------------------------------------

# Database Tables

## users

-   id
-   employee_id
-   name
-   email
-   password
-   role
-   department_id
-   is_active
-   created_at

## departments

-   id
-   name

## categories

-   id
-   name
-   department_id

## complaints

-   id
-   complaint_number
-   title
-   description
-   category_id
-   department_id
-   employee_id
-   technician_id
-   priority
-   status
-   location
-   resolution_note
-   created_at
-   updated_at
-   closed_at

## comments

-   id
-   complaint_id
-   user_id
-   comment
-   created_at

## attachments

-   id
-   complaint_id
-   filename
-   filepath
-   uploaded_by
-   uploaded_at

## complaint_history

-   id
-   complaint_id
-   old_status
-   new_status
-   updated_by
-   updated_at

## notifications

-   id
-   user_id
-   message
-   is_read
-   created_at

## activity_logs

-   id
-   user_id
-   action
-   entity_type
-   entity_id
-   old_value
-   new_value
-   created_at

------------------------------------------------------------------------

# REST API

## Authentication & User Management

-   POST /api/auth/login (Public)
-   POST /api/auth/register (Secure - Admin & Manager only)
-   GET /api/auth/users (Secure - Admin & Manager only)
-   PUT /api/auth/profile (Secure - Self-service)

## Administrator Configuration Controls

-   GET /api/admin/departments
-   POST /api/admin/departments
-   PUT /api/admin/departments/{id}
-   DELETE /api/admin/departments/{id}
-   GET /api/admin/categories
-   POST /api/admin/categories
-   PUT /api/admin/categories/{id}
-   DELETE /api/admin/categories/{id}

## Complaints

-   POST /api/complaints
-   GET /api/complaints
-   GET /api/complaints/{id}
-   PUT /api/complaints/{id}
-   PATCH /api/complaints/{id}/status (Verify & Close / Reopen)
-   DELETE /api/complaints/{id}

## Manager & Admin (Technician Assignment)

-   GET /api/manager/complaints
-   GET /api/manager/technicians
-   POST /api/manager/assign
-   PATCH /api/manager/reassign

## Technician Tasks

-   GET /api/technician/tasks
-   PATCH /api/technician/accept/{id}
-   PATCH /api/technician/progress/{id}
-   PATCH /api/technician/resolve/{id}

## Comments (Routed under Complaints Blueprint)

-   POST /api/complaints/comments
-   GET /api/complaints/comments/{complaintId}

## Attachments & Serving (Routed under Complaints Blueprint)

-   POST /api/complaints/upload (Upload files)
-   GET /api/complaints/attachments/{complaintId} (List files metadata)
-   GET /api/complaints/uploads/{filename} (Serve static raw files)

## Notifications

-   GET /api/notifications
-   PATCH /api/notifications/read/{id}
-   DELETE /api/notifications

## Reports

-   GET /api/reports/summary
-   GET /api/reports/department
-   GET /api/reports/priority
-   GET /api/reports/category

------------------------------------------------------------------------

# Automatic Department Assignment

``` text
Complaint Category
        ↓
Category Table
        ↓
Department
        ↓
Complaint.department_id
```

------------------------------------------------------------------------

# Recommended Flask Packages

-   Flask
-   Flask-SQLAlchemy
-   Flask-Migrate
-   Flask-JWT-Extended
-   Flask-CORS
-   marshmallow
-   python-dotenv
-   psycopg2-binary
-   bcrypt

------------------------------------------------------------------------

# Summary

The backend follows a modular layered architecture with JWT-based
authentication, role-based authorization, SQLAlchemy ORM, PostgreSQL
persistence, and a structured complaint workflow. The design is
scalable, maintainable, and suitable for future enhancements such as
email notifications, QR-based complaint creation, and report export.
