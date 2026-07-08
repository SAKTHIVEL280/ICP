## Project Overview

The Internal Complaint Portal is a web-based application designed for a single organization to manage internal complaints related to IT, Facilities, Equipment, HR, and workplace infrastructure.

Instead of using emails, phone calls, or messaging applications, employees can submit complaints through a centralized platform where every issue is tracked from creation until closure.

The system improves communication between employees, managers, and technicians while maintaining a complete history of every complaint.

---

# Objectives

* Centralize complaint management.
* Allow employees to quickly report issues.
* Automatically route complaints to the correct department.
* Enable technicians to update complaint progress.
* Track every complaint until closure.
* Maintain complaint history.
* Improve accountability and transparency.
* Generate basic management reports.

---

# Target Users

## Employee

* Create complaints
* View own complaints
* Track complaint status
* Add comments
* Upload attachments
* Verify completed work
* View notifications

---

## Technician

* View assigned complaints
* Accept assigned work
* Update complaint progress
* Upload completion evidence
* Resolve complaints

---

## Department Manager

* View department complaints
* Assign technicians
* Reassign complaints
* Monitor complaint progress
* View department reports

---

## Administrator

* Manage users
* Manage departments
* Manage complaint categories
* View all complaints
* Generate reports
* Manage system settings

---

# Complaint Categories

## IT

* Computer
* Laptop
* Printer
* Software Installation
* Network
* Internet
* Email

Department: IT Support

---

## Facilities

* Air Conditioner
* Lighting
* Furniture
* Water Supply
* Washroom
* Meeting Room

Department: Facilities

---

## Equipment

* Machine Failure
* Generator
* Motor
* Conveyor
* Sensor

Department: Maintenance

---

## HR

* Payroll
* Attendance
* ID Card
* Access Card

Department: Human Resources

---

## Safety

* Fire Hazard
* Electrical Hazard
* Emergency Equipment
* Unsafe Workplace

Department: Safety

---

# Complaint Form

### Required Fields

* Complaint Title
* Complaint Description
* Category
* Location
* Priority
* Attachment (Optional)

### Automatically Generated

* Complaint ID
* Department (Based on Category)
* Complaint Status
* Created Date & Time
* Created By

---

# Complaint Priority

The system supports four priority levels.

* Low
* Medium
* High
* Critical

Priority will be stored as an ENUM value in the database.

---

# Complaint Status Workflow

New

↓

Assigned

↓

Accepted

↓

In Progress

↓

Resolved

↓

Employee Verification

↓

Closed

Rejected can only occur before assignment.

Complaint Status will be stored as an ENUM value in the database.

---

# User Roles

The system contains four user roles.

* Employee
* Technician
* Manager
* Administrator

Roles will be stored as an ENUM value in the database.

---

# User Permissions

## Employee

Can

* Create complaints
* View own complaints
* Add comments
* Upload attachments
* Verify completed work

Cannot

* View other complaints
* Assign complaints
* Delete complaints

---

## Technician

Can

* View assigned complaints
* Accept work
* Update status
* Upload completion evidence
* Add comments

Cannot

* Assign complaints
* Delete complaints

---

## Department Manager

Can

* View department complaints
* Assign technicians
* Reassign technicians
* Monitor complaint progress

---

## Administrator

Can perform all operations within the system.

---

# Complaint Workflow

Employee

↓

Create Complaint

↓

Department Automatically Selected

↓

Manager Reviews

↓

Assign Technician

↓

Technician Accepts

↓

Work In Progress

↓

Resolved

↓

Employee Verification

↓

Closed

---

# Dashboard Modules

## Employee Dashboard

* Create Complaint
* My Complaints
* Complaint History
* Notifications
* Profile

---

## Technician Dashboard

* Assigned Complaints
* Pending Work
* Completed Work
* Update Progress

---

## Department Manager Dashboard

* Department Complaints
* Pending Complaints
* Technician Assignment
* Complaint Statistics

---

## Administrator Dashboard

* User Management
* Department Management
* Category Management
* Complaint Management
* Reports
* System Settings

---

# Complaint Details

Each complaint contains

* Complaint ID
* Title
* Description
* Category
* Department
* Location
* Priority
* Current Status
* Raised By
* Assigned Technician
* Created Date
* Last Updated
* Attachments
* Resolution Notes

---

# Notifications

Notifications are generated when

* Complaint Created
* Complaint Assigned
* Complaint Accepted
* Status Updated
* Comment Added
* Complaint Resolved
* Complaint Closed

Recipients

* Employee
* Assigned Technician
* Department Manager
* Administrator

---

# Activity Log

Every important system action is recorded.

Each activity contains

* User
* Action
* Previous Value
* New Value
* Date & Time

Example Actions

* Complaint Created
* Technician Assigned
* Complaint Updated
* Priority Changed
* Complaint Closed

---

# Reports

* Total Complaints
* Open Complaints
* Closed Complaints
* Complaints by Department
* Complaints by Category
* Complaints by Priority
* Monthly Complaint Count

---

# Database Design

The database is normalized to reduce redundancy while remaining simple enough for a training project.

Main Entities

* Department
* Category
* User
* Complaint
* Complaint History
* Comment
* Attachment
* Notification
* Activity Log

The following values will be stored as ENUM types instead of separate tables.

* User Role
* Complaint Status
* Complaint Priority

This reduces unnecessary joins and simplifies database queries.

---

# Technology Stack

## Frontend

* HTML
* CSS
* JavaScript

---

## Backend

* Python (Flask)

---

## Database

* PostgreSQL

---

## Authentication

* JWT Authentication

---

## File Storage

* Local Storage (Development)

---

# Future Enhancements

* QR Code Complaint Registration
* Email Notifications
* Mobile Responsive Design
* Export Reports (PDF / Excel)

---

# Expected Outcome

The Internal Complaint Portal provides a centralized platform for managing employee complaints within a single organization. Every complaint follows a structured workflow from creation to closure, ensuring transparency, accountability, and efficient issue resolution while maintaining a complete history of all actions performed.
