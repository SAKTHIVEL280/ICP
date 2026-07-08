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
├── app.py
├── config.py
├── requirements.txt
│
├── routes/
│   ├── auth_routes.py
│   ├── complaint_routes.py
│   ├── user_routes.py
│   ├── manager_routes.py
│   ├── technician_routes.py
│   ├── admin_routes.py
│   ├── report_routes.py
│   └── notification_routes.py
│
├── controllers/
│   ├── auth_controller.py
│   ├── complaint_controller.py
│   ├── assignment_controller.py
│   ├── report_controller.py
│   └── user_controller.py
│
├── services/
│   ├── auth_service.py
│   ├── complaint_service.py
│   ├── notification_service.py
│   ├── report_service.py
│   └── upload_service.py
│
├── models/
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
├── middleware/
│   ├── auth.py
│   ├── role_required.py
│   └── error_handler.py
│
├── utils/
│   ├── jwt_utils.py
│   ├── validators.py
│   ├── enums.py
│   └── helpers.py
│
├── uploads/
└── migrations/
```

------------------------------------------------------------------------

# Layer Responsibilities

## Routes

-   Receive HTTP requests.
-   Map endpoints to controllers.

## Controllers

-   Validate requests.
-   Call services.
-   Return HTTP responses.
-   No database queries.

## Services

-   Implement business logic.
-   Coordinate database operations.
-   Trigger notifications and logging.

## Models

-   SQLAlchemy ORM models.
-   Represent database tables.

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
-   password_hash
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

## Authentication

-   POST /api/auth/login
-   POST /api/auth/logout
-   GET /api/auth/profile

## Complaints

-   POST /api/complaints
-   GET /api/complaints
-   GET /api/complaints/{id}
-   PUT /api/complaints/{id}
-   PATCH /api/complaints/{id}/status
-   DELETE /api/complaints/{id}

## Manager

-   GET /api/manager/complaints
-   POST /api/manager/assign
-   PATCH /api/manager/reassign

## Technician

-   GET /api/technician/tasks
-   PATCH /api/technician/accept/{id}
-   PATCH /api/technician/progress/{id}
-   PATCH /api/technician/resolve/{id}

## Comments

-   POST /api/comments
-   GET /api/comments/{complaintId}

## Attachments

-   POST /api/upload
-   GET /api/attachments/{complaintId}

## Notifications

-   GET /api/notifications
-   PATCH /api/notifications/read/{id}

## Reports

-   GET /api/reports/summary
-   GET /api/reports/monthly
-   GET /api/reports/department
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
