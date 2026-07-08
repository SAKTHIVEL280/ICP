# Internal Complaint Portal - Frontend Design

## Overview

The frontend is a responsive web application built with HTML, CSS, and
JavaScript. It communicates with the Flask backend through REST APIs
using JWT authentication. The interface is designed according to user
roles: Employee, Technician, Department Manager, and Administrator.

------------------------------------------------------------------------

# Frontend Architecture

``` text
Browser
   │
   ▼
HTML Pages
   │
CSS (Styling)
   │
JavaScript (UI Logic)
   │
Fetch API
   │
JWT Authentication
   │
Flask REST API
```

------------------------------------------------------------------------

# Project Structure

``` text
frontend/
│
├── index.html
├── login.html
├── dashboard.html
│
├── css/
│   ├── style.css
│   ├── login.css
│   ├── dashboard.css
│   ├── forms.css
│   └── tables.css
│
├── js/
│   ├── auth.js
│   ├── dashboard.js
│   ├── complaints.js
│   ├── technician.js
│   ├── manager.js
│   ├── admin.js
│   ├── notifications.js
│   ├── api.js
│   └── utils.js
│
├── assets/
│   ├── images/
│   ├── icons/
│   └── logo/
│
└── uploads/
```

------------------------------------------------------------------------

# UI Modules

## Login

-   Email / Employee ID
-   Password
-   Login button
-   Error messages

## Employee

-   Dashboard
-   Create Complaint
-   My Complaints
-   Complaint History
-   Notifications
-   Profile

## Technician

-   Assigned Complaints
-   Pending Work
-   Completed Work
-   Update Progress
-   Upload Evidence

## Department Manager

-   Dashboard
-   Department Complaints
-   Assign Technician
-   Reassign Technician
-   Complaint Statistics

## Administrator

-   Dashboard
-   User Management
-   Department Management
-   Category Management
-   Complaint Management
-   Reports
-   System Settings

------------------------------------------------------------------------

# Navigation

``` text
Login
  │
  ▼
Dashboard
  ├── Complaints
  ├── Notifications
  ├── Reports
  ├── Profile
  └── Logout
```

Menus are displayed according to the authenticated user's role.

------------------------------------------------------------------------

# Page Layout

``` text
+----------------------------------------+
| Header                                 |
+----------------------------------------+
| Sidebar | Main Content                 |
|         |                              |
|         | Dashboard / Forms / Tables   |
|         |                              |
+----------------------------------------+
| Footer                                 |
+----------------------------------------+
```

------------------------------------------------------------------------

# Reusable Components

-   Header
-   Sidebar
-   Breadcrumb
-   Data Table
-   Search Bar
-   Filter Panel
-   Pagination
-   Modal Dialog
-   Confirmation Dialog
-   Notification Toast
-   File Upload
-   Status Badge
-   Loading Spinner

------------------------------------------------------------------------

# Dashboard Cards

Employee - Total Complaints - Open Complaints - Resolved Complaints -
Closed Complaints

Technician - Assigned Tasks - Pending Tasks - Completed Tasks

Manager - Department Complaints - Unassigned Complaints - Active
Technicians

Administrator - Users - Departments - Categories - Total Complaints

------------------------------------------------------------------------

# Complaint Form

Fields - Complaint Title - Description - Category - Location -
Priority - Attachment

Buttons - Submit - Reset - Cancel

Validation - Required fields - Maximum length - File type and size -
Client-side validation before submission

------------------------------------------------------------------------

# Complaint Details Page

Displays - Complaint Information - Status Timeline - Assigned
Technician - Comments - Attachments - Resolution Notes - Activity
History

Actions depend on the logged-in user's role.

------------------------------------------------------------------------

# Tables

Columns - Complaint ID - Title - Category - Priority - Status - Assigned
Technician - Created Date - Actions

Features - Search - Filter - Sort - Pagination

------------------------------------------------------------------------

# Notifications

-   Complaint Created
-   Assigned
-   Accepted
-   Status Updated
-   Resolved
-   Closed

Unread notifications are highlighted.

------------------------------------------------------------------------

# Authentication Flow

``` text
Login
  ↓
Receive JWT
  ↓
Store Token (Local Storage)
  ↓
Attach Token to API Requests
  ↓
Protected Pages
```

------------------------------------------------------------------------

# API Integration

``` javascript
fetch('/api/complaints', {
  headers: {
    Authorization: 'Bearer ' + token
  }
});
```

------------------------------------------------------------------------

# Responsive Design

Desktop - Sidebar visible

Tablet - Collapsible sidebar

Mobile - Hamburger navigation - Responsive tables - Full-width forms

------------------------------------------------------------------------

# Color Scheme

-   Primary: Blue
-   Success: Green
-   Warning: Orange
-   Error: Red
-   Background: Light Gray
-   Text: Dark Gray

------------------------------------------------------------------------

# Icons

-   Dashboard
-   Complaint
-   User
-   Settings
-   Notifications
-   Reports
-   Logout

------------------------------------------------------------------------

# Frontend Workflow

``` text
User Login
   ↓
Dashboard
   ↓
Select Module
   ↓
API Request
   ↓
Backend Response
   ↓
Update UI
```

------------------------------------------------------------------------

# Summary

The frontend follows a modular structure with reusable UI components,
role-based navigation, responsive layouts, client-side validation, and
REST API integration using JWT authentication. The design prioritizes
usability, maintainability, and scalability.
