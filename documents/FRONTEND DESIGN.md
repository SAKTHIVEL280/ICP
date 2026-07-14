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
├── index.html                  # Landing gatekeeper (auth status check & redirect)
├── login.html                  # Sign-in form template
├── dashboard.html              # Dynamic single-page dashboard container
│
├── css/
│   └── style.css               # Short custom overrides (sidebar size, timeline layout)
│
└── js/
    ├── auth.js                 # Session manager: JWT token decoding, padding, & guards
    └── dashboard.js            # Consolidated interface driver: fetches list, modals, CSS charts
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
-   Technician Assignment (Shared with Manager)
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

Unread notifications are highlighted. The dropdown contains a static top bar with a "Clear All" button allowing users to delete all notifications instantly.

### Live Toast Alerts
When new unread notifications are received during active sessions, a dynamic Bootstrap Toast message card floats into the bottom-right corner of the screen, alerting users in real-time without interrupting their workflow.

### Profile Settings (Self-Service)
Any logged-in user can click on the "Edit Profile" button located underneath their name in the sidebar. This opens a modal where they can change their display name or update their password (which requires entering their current password for security verification).

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

Desktop - Sidebar visible on the left side of the content viewport (width: 240px).

Mobile & Tablet (<= 768px) - Responsive stacked layout. The flex direction transitions to vertical, stacking the sidebar above the main content window. Table components are responsive, and form inputs stretch to full width. The notification bell dropdown has a maximum width clamp (90vw) with word-wrapping enabled to prevent viewport overflow.

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
