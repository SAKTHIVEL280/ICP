// frontend/js/dashboard.js
// This single consolidated script handles the entire dashboard logic for all roles.
// It is designed to be clean, simple, and easy to explain to others.

// Global state variables
const API_BASE_URL = "http://127.0.0.1:5000/api";
let currentUser = null;
let currentComplaintId = null; // Stores the ID of the complaint currently open in the details view
let departmentTechnicians = [];  // Stores the list of technicians for managers to select from

// -------------------------------------------------------------
// 1. Initial Page Load & Event Listeners setup
// -------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    // Force user to log in if they have no active session (guard)
    currentUser = requireAuth();
    if (!currentUser) return;

    // Render the logged-in user profile details in the sidebar
    document.getElementById("user-name-display").innerText = currentUser.name;
    document.getElementById("user-role-display").innerText = currentUser.role;

    // Set up menus and buttons depending on the user's role
    setupSidebarMenus();

    // Register click handlers for sidebar menu tab switches
    document.querySelectorAll("[data-tab]").forEach(item => {
        item.addEventListener("click", () => {
            const tabId = item.getAttribute("data-tab");
            switchTab(tabId);
        });
    });

    // Logout button handler
    document.getElementById("logout-btn").addEventListener("click", logoutUser);

    // New Complaint form submission handler
    document.getElementById("new-complaint-form").addEventListener("submit", handleComplaintSubmit);

    // Comment submission form handler in details tab
    document.getElementById("comment-submit-form").addEventListener("submit", handleCommentSubmit);

    // Attachment upload form handler in details tab
    document.getElementById("upload-submit-form").addEventListener("submit", handleAttachmentSubmit);

    // New User registration form submission handler
    document.getElementById("create-user-form").addEventListener("submit", handleUserCreateSubmit);

    // Profile form submission handler
    document.getElementById("profile-form").addEventListener("submit", (e) => {
        e.preventDefault();
        submitProfileUpdate();
    });

    // Department CRUD form submission handler
    document.getElementById("dept-form").addEventListener("submit", (e) => {
        e.preventDefault();
        submitDepartmentForm();
    });

    // Category CRUD form submission handler
    document.getElementById("category-form").addEventListener("submit", (e) => {
        e.preventDefault();
        submitCategoryForm();
    });

    // Start pulling notifications badge
    loadNotifications();
    // Poll notifications list every 15 seconds
    setInterval(loadNotifications, 15000);

    // Default tab is Dashboard Home
    switchTab("tab-home");
});

// -------------------------------------------------------------
// 2. Central API Fetch Wrapper
// -------------------------------------------------------------
async function apiFetch(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    options.headers = options.headers || {};
    
    // Add token authorization header
    const token = localStorage.getItem("access_token");
    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }

    // Convert object payload to JSON string if it is not a FormData upload
    if (options.body && typeof options.body === "object" && !(options.body instanceof FormData)) {
        options.body = JSON.stringify(options.body);
        options.headers["Content-Type"] = "application/json";
    }

    const response = await fetch(url, options);

    // Global session expiration handler (401)
    if (response.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "login.html";
        throw new Error("Session expired. Please log in again.");
    }

    // Parse JSON response body
    let data = {};
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
        data = await response.json();
    } else {
        data = await response.text();
    }

    if (!response.ok) {
        throw new Error(data.error || data.message || "Request failed");
    }

    return data;
}

// -------------------------------------------------------------
// 3. Tab Routing / Switching Controller
// -------------------------------------------------------------
function switchTab(tabId) {
    // Clear any active alert banners
    hideAlerts();

    // Remove active styling from all menu items
    document.querySelectorAll("[data-tab]").forEach(item => {
        item.classList.remove("active");
    });
    
    // Add active class to the clicked sidebar menu item
    const activeMenuItem = document.querySelector(`[data-tab="${tabId}"]`);
    if (activeMenuItem) {
        activeMenuItem.classList.add("active");
    }

    // Hide all tab sections using Bootstrap's d-none utility
    document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.add("d-none");
    });

    // Show the target tab section
    const targetPane = document.getElementById(tabId);
    if (targetPane) {
        targetPane.classList.remove("d-none");
    }

    // Trigger tab-specific loaders
    if (tabId === "tab-home") {
        loadHomeStats();
    } else if (tabId === "tab-list") {
        loadComplaintsList();
    } else if (tabId === "tab-new") {
        loadCategoriesDropdown();
    } else if (tabId === "tab-reports") {
        loadReportsAndCharts();
    } else if (tabId === "tab-users") {
        loadUsersList();
    } else if (tabId === "tab-admin-settings") {
        loadAdminSettings();
    }
}

// -------------------------------------------------------------
// 4. Role-based Sidebar and Header Controller
// -------------------------------------------------------------
function setupSidebarMenus() {
    const role = currentUser.role;

    // Hide all items with class "role-restricted" first
    document.querySelectorAll(".role-restricted").forEach(el => el.classList.add("d-none"));

    // Display views based on role values
    if (role === "Employee") {
        document.querySelectorAll(".role-employee").forEach(el => el.classList.remove("d-none"));
        document.getElementById("nav-complaints-text").innerText = "My Complaints";
    } else if (role === "Technician") {
        document.querySelectorAll(".role-technician").forEach(el => el.classList.remove("d-none"));
        document.getElementById("nav-complaints-text").innerText = "My Tasks";
    } else if (role === "Manager") {
        document.querySelectorAll(".role-manager").forEach(el => el.classList.remove("d-none"));
        document.getElementById("nav-complaints-text").innerText = "Department Tickets";
    } else if (role === "Administrator") {
        // Admins can access all tabs
        document.querySelectorAll(".role-restricted").forEach(el => el.classList.remove("d-none"));
        document.getElementById("nav-complaints-text").innerText = "All Complaints";
    }
}

// -------------------------------------------------------------
// 5. Dashboard Home Summary Loader
// -------------------------------------------------------------
async function loadHomeStats() {
    try {
        let total = 0, open = 0, resolved = 0, closed = 0;
        const role = currentUser.role;

        // Managers and Admins get aggregated reports from the database summary
        if (role === "Manager" || role === "Administrator") {
            const summary = await apiFetch("/reports/summary", { method: "GET" });
            total = summary.total;
            open = summary.open;
            resolved = summary.resolved;
            closed = summary.closed;
        } else {
            // Employees and Technicians calculate stats on their own list client-side
            const complaints = await apiFetch("/complaints", { method: "GET" });
            total = complaints.length;
            open = complaints.filter(c => c.status !== "Closed" && c.status !== "Rejected").length;
            resolved = complaints.filter(c => c.status === "Resolved").length;
            closed = complaints.filter(c => c.status === "Closed").length;
        }

        // Write counts directly into card HTML slots
        document.getElementById("stat-total").innerText = total;
        document.getElementById("stat-open").innerText = open;
        document.getElementById("stat-resolved").innerText = resolved;
        document.getElementById("stat-closed").innerText = closed;

    } catch (err) {
        showError(err.message);
    }
}

// -------------------------------------------------------------
// 6. Category Dropdown Loader
// -------------------------------------------------------------
async function loadCategoriesDropdown() {
    try {
        const categories = await apiFetch("/complaints/categories", { method: "GET" });
        const select = document.getElementById("comp-category");
        select.innerHTML = '<option value="">-- Choose Category --</option>';

        categories.forEach(cat => {
            const option = document.createElement("option");
            option.value = cat.id;
            option.innerText = `${cat.name} (${cat.department_name})`;
            select.appendChild(option);
        });
    } catch (err) {
        showError("Failed to load categories: " + err.message);
    }
}

// -------------------------------------------------------------
// 7. Complaints & Tasks Table Loader
// -------------------------------------------------------------
async function loadComplaintsList() {
    const tableBody = document.getElementById("complaints-table-body");
    tableBody.innerHTML = '<tr><td colspan="7" class="text-center">Loading...</td></tr>';
    
    try {
        let endpoint = "/complaints";
        const role = currentUser.role;

        // If the user is a manager, fetch from the manager routing endpoint
        if (role === "Manager") {
            endpoint = "/manager/complaints";
        } else if (role === "Technician") {
            endpoint = "/technician/tasks";
        }

        const complaints = await apiFetch(endpoint, { method: "GET" });
        tableBody.innerHTML = "";

        if (complaints.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">No complaints found.</td></tr>`;
            return;
        }

        // Render rows
        complaints.forEach(c => {
            const row = document.createElement("tr");

            // Format date string cleanly
            const dateStr = c.created_at ? c.created_at.split(" ")[0] : "N/A";

            // Define custom columns based on role
            let actionButtonsHTML = `<button class="btn btn-sm btn-outline-primary" onclick="loadComplaintDetails(${c.id})">View</button>`;
            
            // Managers and Administrators get assignment shortcuts
            if (role === "Manager" || role === "Administrator") {
                if (!c.technician) {
                    actionButtonsHTML += ` <button class="btn btn-sm btn-warning ms-1" onclick="openAssignmentModal(${c.id}, null)">Assign</button>`;
                } else {
                    actionButtonsHTML += ` <button class="btn btn-sm btn-outline-secondary ms-1" onclick="openAssignmentModal(${c.id}, ${c.technician.id})">Reassign</button>`;
                }
            }

            // Technicians get quick progress button options
            if (role === "Technician") {
                if (c.status === "Assigned") {
                    actionButtonsHTML += ` <button class="btn btn-sm btn-info ms-1" onclick="handleAcceptTask(${c.id})">Accept</button>`;
                } else if (c.status === "Accepted") {
                    actionButtonsHTML += ` <button class="btn btn-sm btn-primary ms-1" onclick="handleStartProgress(${c.id})">Start</button>`;
                } else if (c.status === "In Progress") {
                    actionButtonsHTML += ` <button class="btn btn-sm btn-success ms-1" onclick="openResolveModal(${c.id})">Resolve</button>`;
                }
            }

            row.innerHTML = `
                <td><strong>${sanitizeText(c.complaint_number)}</strong></td>
                <td>${sanitizeText(c.title)}</td>
                <td>${sanitizeText(c.category)}</td>
                <td><span class="badge ${getPriorityBadgeClass(c.priority)}">${sanitizeText(c.priority)}</span></td>
                <td><span class="badge ${getStatusBadgeClass(c.status)}">${sanitizeText(c.status)}</span></td>
                <td>${dateStr}</td>
                <td>${actionButtonsHTML}</td>
            `;

            tableBody.appendChild(row);
        });

    } catch (err) {
        showError(err.message);
    }
}

// -------------------------------------------------------------
// 8. Single Complaint Detailed View Loader
// -------------------------------------------------------------
async function loadComplaintDetails(complaintId) {
    hideAlerts();
    try {
        const c = await apiFetch(`/complaints/${complaintId}`, { method: "GET" });
        currentComplaintId = c.id;

        // Switch to the Details tab view
        document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.add("d-none"));
        document.getElementById("tab-details").classList.remove("d-none");

        // Write meta fields
        document.getElementById("det-number").innerText = c.complaint_number;
        document.getElementById("det-title").innerText = c.title;
        document.getElementById("det-desc").innerText = c.description;
        document.getElementById("det-category").innerText = c.category;
        document.getElementById("det-department").innerText = c.department;
        document.getElementById("det-location").innerText = c.location;
        document.getElementById("det-created").innerText = c.created_at || "N/A";
        document.getElementById("det-updated").innerText = c.updated_at || "N/A";
        document.getElementById("det-closed").innerText = c.closed_at || "Open";

        // Badges
        const priorityContainer = document.getElementById("det-priority");
        priorityContainer.innerHTML = `<span class="badge ${getPriorityBadgeClass(c.priority)}">${sanitizeText(c.priority)}</span>`;
        
        const statusContainer = document.getElementById("det-status");
        statusContainer.innerHTML = `<span class="badge ${getStatusBadgeClass(c.status)}">${sanitizeText(c.status)}</span>`;

        // Users names
        document.getElementById("det-raised").innerText = c.employee ? c.employee.name : "N/A";
        document.getElementById("det-tech").innerText = c.technician ? c.technician.name : "Unassigned";

        // Resolution Notes
        const resRow = document.getElementById("det-res-row");
        if (c.resolution_note) {
            document.getElementById("det-resolution").innerText = c.resolution_note;
            resRow.classList.remove("d-none");
        } else {
            resRow.classList.add("d-none");
        }

        // Render Verify Actions Panel (Show only to ticket owner if ticket status is Resolved)
        const verifyPanel = document.getElementById("verification-panel");
        if (c.status === "Resolved" && currentUser.id === c.employee.id) {
            verifyPanel.classList.remove("d-none");
        } else {
            verifyPanel.classList.add("d-none");
        }

        // Render Comments list
        renderCommentsList(c.comments);

        // Render Attachments list
        renderAttachmentsList(c.attachments);

        // Render History Timeline
        renderTimelineList(c.history);

    } catch (err) {
        showError(err.message);
    }
}

// -------------------------------------------------------------
// 9. Form Submission Event Handlers
// -------------------------------------------------------------
async function handleComplaintSubmit(e) {
    e.preventDefault();

    const title = document.getElementById("comp-title").value;
    const description = document.getElementById("comp-description").value;
    const category_id = parseInt(document.getElementById("comp-category").value);
    const location = document.getElementById("comp-location").value;
    const priority = document.getElementById("comp-priority").value;
    const fileInput = document.getElementById("comp-file");
    const submitBtn = document.getElementById("comp-submit-btn");

    try {
        submitBtn.disabled = true;
        submitBtn.innerText = "Submitting...";

        // 1. Submit ticket details
        const data = await apiFetch("/complaints", {
            method: "POST",
            body: { title, description, category_id, location, priority }
        });

        // 2. Upload file if selected
        if (fileInput && fileInput.files.length > 0) {
            submitBtn.innerText = "Uploading file...";
            const formData = new FormData();
            formData.append("file", fileInput.files[0]);
            formData.append("complaint_id", data.complaint.id);

            await apiFetch("/complaints/upload", {
                method: "POST",
                body: formData
            });
        }

        showSuccess("Complaint submitted successfully!");
        e.target.reset();
        switchTab("tab-list");

    } catch (err) {
        showError(err.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = "Submit Complaint";
    }
}

async function handleCommentSubmit(e) {
    e.preventDefault();
    const commentInput = document.getElementById("comment-text");
    const text = commentInput.value;

    if (!text || text.trim() === "") return;

    try {
        await apiFetch("/complaints/comments", {
            method: "POST",
            body: {
                complaint_id: currentComplaintId,
                comment: text
            }
        });

        commentInput.value = "";
        // Refresh details view
        await loadComplaintDetails(currentComplaintId);
    } catch (err) {
        showError(err.message);
    }
}

async function handleAttachmentSubmit(e) {
    e.preventDefault();
    const fileInput = document.getElementById("upload-file");
    if (!fileInput || fileInput.files.length === 0) return;

    try {
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        formData.append("complaint_id", currentComplaintId);

        await apiFetch("/complaints/upload", {
            method: "POST",
            body: formData
        });

        fileInput.value = "";
        showSuccess("File uploaded successfully!");
        await loadComplaintDetails(currentComplaintId);
    } catch (err) {
        showError(err.message);
    }
}

// -------------------------------------------------------------
// 10. Technician Status Transition Event Handlers
// -------------------------------------------------------------
async function handleAcceptTask(complaintId) {
    try {
        await apiFetch(`/technician/accept/${complaintId}`, { method: "PATCH" });
        showSuccess("Task accepted.");
        await loadComplaintsList();
    } catch (err) {
        showError(err.message);
    }
}

async function handleStartProgress(complaintId) {
    try {
        await apiFetch(`/technician/progress/${complaintId}`, { method: "PATCH" });
        showSuccess("Task marked as In Progress.");
        await loadComplaintsList();
    } catch (err) {
        showError(err.message);
    }
}

function openResolveModal(complaintId) {
    window.targetResolutionId = complaintId;
    document.getElementById("resolution-note").value = "";
    
    // Open Bootstrap modal using vanilla bootstrap JS
    const modal = new bootstrap.Modal(document.getElementById("resolveModal"));
    modal.show();
}

async function submitTaskResolution() {
    const note = document.getElementById("resolution-note").value;
    if (!note || note.trim() === "") {
        alert("Resolution note is required.");
        return;
    }

    try {
        await apiFetch(`/technician/resolve/${window.targetResolutionId}`, {
            method: "PATCH",
            body: { resolution_note: note }
        });

        // Hide resolution modal
        const modalElement = document.getElementById("resolveModal");
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) modalInstance.hide();

        showSuccess("Ticket marked as Resolved.");
        
        // Refresh appropriate view
        if (currentComplaintId === window.targetResolutionId) {
            await loadComplaintDetails(currentComplaintId);
        } else {
            await loadComplaintsList();
        }
    } catch (err) {
        showError(err.message);
    }
}

// -------------------------------------------------------------
// 11. Manager Actions (Technician Assignment Modals)
// -------------------------------------------------------------
async function openAssignmentModal(complaintId, currentTechId) {
    window.targetAssignmentId = complaintId;
    window.isReassignment = currentTechId !== null;

    try {
        // Fetch active technicians list in the target department
        const technicians = await apiFetch("/manager/technicians?complaint_id=" + complaintId, { method: "GET" });
        
        const select = document.getElementById("tech-select");
        select.innerHTML = '<option value="">-- Choose Technician --</option>';

        technicians.forEach(t => {
            const option = document.createElement("option");
            option.value = t.id;
            option.innerText = t.name;
            if (currentTechId && t.id === currentTechId) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        // Show Bootstrap modal
        const modal = new bootstrap.Modal(document.getElementById("assignModal"));
        modal.show();

    } catch (err) {
        showError(err.message);
    }
}

async function submitTechnicianAssignment() {
    const techId = document.getElementById("tech-select").value;
    if (!techId) {
        alert("Please select a technician.");
        return;
    }

    const complaintId = window.targetAssignmentId;
    const isReassign = window.isReassignment;

    try {
        const endpoint = isReassign ? "/manager/reassign" : "/manager/assign";
        const method = isReassign ? "PATCH" : "POST";

        await apiFetch(endpoint, {
            method: method,
            body: {
                complaint_id: complaintId,
                technician_id: parseInt(techId)
            }
        });

        // Close modal
        const modalElement = document.getElementById("assignModal");
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) modalInstance.hide();

        showSuccess("Technician assigned successfully.");
        await loadComplaintsList();
    } catch (err) {
        showError(err.message);
    }
}

// -------------------------------------------------------------
// 12. Employee Actions (Approve & Close / Reopen)
// -------------------------------------------------------------
async function handleVerify(action) {
    try {
        await apiFetch(`/complaints/${currentComplaintId}/status`, {
            method: "PATCH",
            body: { action }
        });
        showSuccess(`Ticket state updated: ${action === "Close" ? "Closed" : "Reopened"}.`);
        await loadComplaintDetails(currentComplaintId);
    } catch (err) {
        showError(err.message);
    }
}

// -------------------------------------------------------------
// 13. Notifications Loader
// -------------------------------------------------------------
async function clearAllNotifications(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    try {
        await apiFetch("/notifications", { method: "DELETE" });
        showSuccess("All notifications cleared successfully.");
        await loadNotifications();
    } catch (err) {
        showError(err.message);
    }
}
window.clearAllNotifications = clearAllNotifications;

let lastNotifIds = new Set();

async function loadNotifications() {
    try {
        const list = await apiFetch("/notifications", { method: "GET" });
        const unreadList = list.filter(n => !n.is_read);
        const unreadCount = unreadList.length;

        // Check for new notifications to show toast alerts
        let isFirstLoad = lastNotifIds.size === 0;
        unreadList.forEach(n => {
            if (!lastNotifIds.has(n.id)) {
                lastNotifIds.add(n.id);
                if (!isFirstLoad) {
                    showToastNotification(n.message, "info");
                }
            }
        });

        // Update badge counter in the top bar
        const badge = document.getElementById("notif-badge");
        if (unreadCount > 0) {
            badge.innerText = unreadCount;
            badge.classList.remove("d-none");
        } else {
            badge.classList.add("d-none");
        }

        // Render drop-down elements
        const dropdownList = document.getElementById("notif-dropdown-list");
        dropdownList.innerHTML = "";

        if (list.length === 0) {
            dropdownList.innerHTML = '<li><a class="dropdown-item text-muted" href="#">No notifications.</a></li>';
            return;
        }

        // Render up to 5 elements
        const displayList = list.slice(0, 5);
        displayList.forEach(n => {
            const li = document.createElement("li");
            const a = document.createElement("a");
            a.className = `dropdown-item text-wrap ${n.is_read ? '' : 'fw-bold'}`;
            a.style.whiteSpace = "normal";
            a.href = "#";
            a.innerText = n.message;
            
            // Mark as read when clicked
            a.addEventListener("click", async (e) => {
                e.preventDefault();
                await apiFetch(`/notifications/read/${n.id}`, { method: "PATCH" });
                await loadNotifications();
            });

            li.appendChild(a);
            dropdownList.appendChild(li);
        });

    } catch (err) {
        console.error("Notifications fetch failed:", err);
    }
}

// -------------------------------------------------------------
// 14. Reports & CSS Chart Progress Bar Renderer
// -------------------------------------------------------------
async function loadReportsAndCharts() {
    try {
        // Fetch report data
        const summary = await apiFetch("/reports/summary", { method: "GET" });
        const depts = await apiFetch("/reports/department", { method: "GET" });
        const priorities = await apiFetch("/reports/priority", { method: "GET" });
        const categories = await apiFetch("/reports/category", { method: "GET" });

        // A. Summary table counts
        document.getElementById("rep-total").innerText = summary.total;
        document.getElementById("rep-open").innerText = summary.open;
        document.getElementById("rep-resolved").innerText = summary.resolved;
        document.getElementById("rep-closed").innerText = summary.closed;

        // B. Departments progress bars (CSS Chart)
        const deptContainer = document.getElementById("rep-dept-chart");
        deptContainer.innerHTML = "";
        const maxDeptCount = Math.max(...depts.map(d => d.count), 1);
        
        depts.forEach(d => {
            const pct = Math.round((d.count / maxDeptCount) * 100);
            const row = document.createElement("div");
            row.className = "mb-3";
            row.innerHTML = `
                <div class="d-flex justify-content-between mb-1">
                    <span>${sanitizeText(d.department)}</span>
                    <span class="fw-bold">${d.count}</span>
                </div>
                <div class="progress" style="height: 12px;">
                    <div class="progress-bar bg-primary" role="progressbar" style="width: ${pct}%"></div>
                </div>
            `;
            deptContainer.appendChild(row);
        });

        // C. Priorities progress bars (CSS Chart)
        const priorityContainer = document.getElementById("rep-priority-chart");
        priorityContainer.innerHTML = "";
        const maxPriorityCount = Math.max(...priorities.map(p => p.count), 1);
        
        priorities.forEach(p => {
            const pct = Math.round((p.count / maxPriorityCount) * 100);
            
            // Map priority color scheme
            let color = "bg-success";
            const cleanPriority = p.priority.toLowerCase();
            if (cleanPriority === "medium") color = "bg-info";
            else if (cleanPriority === "high") color = "bg-warning";
            else if (cleanPriority === "critical") color = "bg-danger";

            const row = document.createElement("div");
            row.className = "mb-3";
            row.innerHTML = `
                <div class="d-flex justify-content-between mb-1">
                    <span>${sanitizeText(p.priority)}</span>
                    <span class="fw-bold">${p.count}</span>
                </div>
                <div class="progress" style="height: 12px;">
                    <div class="progress-bar ${color}" role="progressbar" style="width: ${pct}%"></div>
                </div>
            `;
            priorityContainer.appendChild(row);
        });

        // D. Category list table
        const categoryList = document.getElementById("rep-category-list");
        categoryList.innerHTML = "";
        categories.forEach(cat => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";
            li.innerHTML = `
                <span>${sanitizeText(cat.category)}</span>
                <span class="badge bg-primary rounded-pill">${cat.count}</span>
            `;
            categoryList.appendChild(li);
        });

    } catch (err) {
        showError(err.message);
    }
}

// -------------------------------------------------------------
// 15. Helper Template Rendering Functions
// -------------------------------------------------------------
function renderCommentsList(comments) {
    const container = document.getElementById("comments-container");
    container.innerHTML = "";

    if (comments.length === 0) {
        container.innerHTML = '<p class="text-muted small">No comments yet.</p>';
        return;
    }

    comments.forEach(c => {
        const item = document.createElement("div");
        item.className = "comment-box";
        item.innerHTML = `
            <div class="comment-meta">
                <strong>${sanitizeText(c.author_name)}</strong> (${sanitizeText(c.author_role)}) &bull; ${c.created_at}
            </div>
            <div class="comment-text">${sanitizeText(c.comment)}</div>
        `;
        container.appendChild(item);
    });
}

function renderAttachmentsList(attachments) {
    const container = document.getElementById("attachments-container");
    container.innerHTML = "";

    if (attachments.length === 0) {
        container.innerHTML = '<p class="text-muted small">No attachments uploaded.</p>';
        return;
    }

    attachments.forEach(att => {
        const fileUrl = `${API_BASE_URL}/complaints/uploads/${att.filepath}`;
        const item = document.createElement("div");
        item.className = "d-flex justify-content-between align-items-center border rounded p-2 mb-2 bg-light small";
        item.innerHTML = `
            <span><i class="bi bi-paperclip"></i> <a href="${fileUrl}" target="_blank" class="text-decoration-none">${sanitizeText(att.filename)}</a></span>
            <span class="text-muted">by ${sanitizeText(att.uploaded_by_name)}</span>
        `;
        container.appendChild(item);
    });
}

function renderTimelineList(history) {
    const container = document.getElementById("timeline-container");
    container.innerHTML = "";

    history.forEach(h => {
        const item = document.createElement("div");
        item.className = "timeline-item";
        
        const oldState = h.old_status ? `<span class="badge ${getStatusBadgeClass(h.old_status)}">${sanitizeText(h.old_status)}</span>` : '<span class="badge bg-light text-muted">None</span>';
        const newState = `<span class="badge ${getStatusBadgeClass(h.new_status)}">${sanitizeText(h.new_status)}</span>`;

        item.innerHTML = `
            <div class="timeline-marker"></div>
            <div class="timeline-body small">
                <div>Status changed: ${oldState} &rarr; ${newState}</div>
                <div class="text-muted">by ${sanitizeText(h.updated_by_name)} on ${h.updated_at}</div>
            </div>
        `;
        container.appendChild(item);
    });
}

// -------------------------------------------------------------
// 16. Utility Helpers (Badge mappings & Input security)
// -------------------------------------------------------------
function getStatusBadgeClass(status) {
    const s = status.toLowerCase();
    if (s === "new") return "bg-primary text-white";
    if (s === "assigned") return "bg-secondary text-white";
    if (s === "accepted") return "bg-info text-dark";
    if (s === "in progress") return "bg-warning text-dark";
    if (s === "resolved") return "bg-success text-white";
    if (s === "closed") return "bg-dark text-white";
    if (s === "rejected") return "bg-danger text-white";
    return "bg-light text-dark";
}

function getPriorityBadgeClass(priority) {
    const p = priority.toLowerCase();
    if (p === "low") return "bg-success text-white";
    if (p === "medium") return "bg-primary text-white";
    if (p === "high") return "bg-warning text-dark";
    if (p === "critical") return "bg-danger text-white";
    return "bg-light text-dark";
}

function sanitizeText(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.innerText = text.toString();
    return div.innerHTML;
}

// -------------------------------------------------------------
// 17. Page Warning Alert Banners
// -------------------------------------------------------------
function showSuccess(msg) {
    const alertBox = document.getElementById("success-alert-banner");
    alertBox.innerText = msg;
    alertBox.classList.remove("d-none");
    // Scroll window to top so user sees the message
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function showError(msg) {
    const alertBox = document.getElementById("error-alert-banner");
    alertBox.innerText = msg;
    alertBox.classList.remove("d-none");
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function hideAlerts() {
    const successBox = document.getElementById("success-alert-banner");
    const errorBox = document.getElementById("error-alert-banner");
    if (successBox) successBox.classList.add("d-none");
    if (errorBox) errorBox.classList.add("d-none");
}

// -------------------------------------------------------------
// 18. User Management Console Loader & Handlers (Manager & Admin)
// -------------------------------------------------------------
async function loadUsersList() {
    const tableBody = document.getElementById("users-table-body");
    tableBody.innerHTML = '<tr><td colspan="8" class="text-center">Loading user records...</td></tr>';
    
    try {
        const users = await apiFetch("/auth/users", { method: "GET" });
        window.usersList = users; // Save globally for easy modal lookups
        tableBody.innerHTML = "";

        if (users.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">No users registered in your scope.</td></tr>`;
            return;
        }

        users.forEach(u => {
            const row = document.createElement("tr");
            
            const statusBadge = u.is_active 
                ? '<span class="badge bg-success">Active</span>' 
                : '<span class="badge bg-secondary">Inactive</span>';

            let actionsHtml = '<span class="text-muted small">N/A</span>';
            if (currentUser.role === "Administrator") {
                const deleteBtn = u.id === 1 
                    ? '<button class="btn btn-sm btn-outline-secondary ms-1" disabled>Delete</button>'
                    : `<button class="btn btn-sm btn-outline-danger ms-1" onclick="handleDeleteUser(${u.id})">Delete</button>`;
                actionsHtml = `
                    <button class="btn btn-sm btn-outline-primary" onclick="openEditUserModal(${u.id})">Edit</button>${deleteBtn}
                `;
            }

            row.innerHTML = `
                <td>${u.id}</td>
                <td><strong>${sanitizeText(u.employee_id)}</strong></td>
                <td>${sanitizeText(u.name)}</td>
                <td>${sanitizeText(u.email)}</td>
                <td><span class="badge bg-primary">${sanitizeText(u.role)}</span></td>
                <td>${sanitizeText(u.department_name)}</td>
                <td>${statusBadge}</td>
                <td>${actionsHtml}</td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        showError("Failed to load user accounts: " + err.message);
    }
}

async function openCreateUserModal() {
    const form = document.getElementById("create-user-form");
    form.reset();
    window.editingUserId = null;

    document.getElementById("createUserModalLabel").innerText = "Register New User Account";
    document.getElementById("usr-submit-btn").innerText = "Register User";
    document.getElementById("usr-status-group").classList.add("d-none");
    
    const pwdInput = document.getElementById("usr-password");
    pwdInput.placeholder = "Minimum 6 characters";
    document.getElementById("usr-password-label").innerText = "Password *";

    const role = currentUser.role;
    const deptGroup = document.getElementById("usr-dept-group");
    const deptSelect = document.getElementById("usr-dept");
    const roleSelect = document.getElementById("usr-role");

    roleSelect.disabled = false;
    deptSelect.disabled = false;

    try {
        const categories = await apiFetch("/complaints/categories", { method: "GET" });
        deptSelect.innerHTML = '<option value="">-- Choose Department --</option>';
        
        const depts = {};
        categories.forEach(c => {
            depts[c.department_id] = c.department_name;
        });

        for (const [id, name] of Object.entries(depts)) {
            const opt = document.createElement("option");
            opt.value = id;
            opt.innerText = name;
            deptSelect.appendChild(opt);
        }

        if (role === "Manager") {
            deptGroup.classList.add("d-none");
            deptSelect.removeAttribute("required");
            roleSelect.innerHTML = `
                <option value="Employee">Employee</option>
                <option value="Technician">Technician</option>
            `;
        } else if (role === "Administrator") {
            deptGroup.classList.remove("d-none");
            deptSelect.setAttribute("required", "required");
            roleSelect.innerHTML = `
                <option value="Employee">Employee</option>
                <option value="Technician">Technician</option>
                <option value="Manager">Manager</option>
                <option value="Administrator">Administrator</option>
            `;
        }

        const modal = new bootstrap.Modal(document.getElementById("createUserModal"));
        modal.show();

    } catch (err) {
        showError("Failed to initialize registration form: " + err.message);
    }
}

async function openEditUserModal(userId) {
    try {
        const u = window.usersList.find(x => x.id === userId);
        if (!u) return;

        window.editingUserId = userId;

        document.getElementById("createUserModalLabel").innerText = "Edit User Details";
        document.getElementById("usr-submit-btn").innerText = "Save Changes";

        const statusGroup = document.getElementById("usr-status-group");
        statusGroup.classList.remove("d-none");
        document.getElementById("usr-status").value = u.is_active ? "true" : "false";

        const pwdInput = document.getElementById("usr-password");
        pwdInput.value = "";
        pwdInput.placeholder = "Leave blank to keep current password";
        document.getElementById("usr-password-label").innerText = "Password (Optional)";

        document.getElementById("usr-name").value = u.name;
        document.getElementById("usr-email").value = u.email;

        const roleSelect = document.getElementById("usr-role");
        roleSelect.innerHTML = `
            <option value="Employee">Employee</option>
            <option value="Technician">Technician</option>
            <option value="Manager">Manager</option>
            <option value="Administrator">Administrator</option>
        `;
        roleSelect.value = u.role;

        const deptGroup = document.getElementById("usr-dept-group");
        const deptSelect = document.getElementById("usr-dept");
        deptGroup.classList.remove("d-none");
        deptSelect.setAttribute("required", "required");

        const categories = await apiFetch("/complaints/categories", { method: "GET" });
        deptSelect.innerHTML = '<option value="">-- Choose Department --</option>';
        
        const depts = {};
        categories.forEach(c => {
            depts[c.department_id] = c.department_name;
        });

        for (const [id, name] of Object.entries(depts)) {
            const opt = document.createElement("option");
            opt.value = id;
            opt.innerText = name;
            deptSelect.appendChild(opt);
        }
        deptSelect.value = u.department_id || "";

        if (userId === 1) {
            roleSelect.disabled = true;
            deptSelect.disabled = true;
            statusGroup.classList.add("d-none");
        } else {
            roleSelect.disabled = false;
            deptSelect.disabled = false;
        }

        const modal = new bootstrap.Modal(document.getElementById("createUserModal"));
        modal.show();

    } catch (err) {
        showError("Failed to load user details: " + err.message);
    }
}

async function handleUserCreateSubmit(e) {
    e.preventDefault();

    const name = document.getElementById("usr-name").value;
    const email = document.getElementById("usr-email").value;
    const password = document.getElementById("usr-password").value;
    const role = document.getElementById("usr-role").value;
    
    const deptSelect = document.getElementById("usr-dept");
    const department_id = (currentUser.role === "Administrator" && deptSelect.value) 
        ? parseInt(deptSelect.value) 
        : null;

    if (!window.editingUserId && (!password || password.trim() === "")) {
        alert("Password is required for new registrations.");
        return;
    }

    const submitBtn = document.getElementById("usr-submit-btn");

    try {
        submitBtn.disabled = true;
        
        if (window.editingUserId) {
            submitBtn.innerText = "Saving Changes...";
            
            const is_active = document.getElementById("usr-status").value === "true";
            const payload = { name, email, role, department_id, is_active };
            if (password && password.trim() !== "") {
                payload.password = password;
            }

            await apiFetch(`/auth/users/${window.editingUserId}`, {
                method: "PUT",
                body: payload
            });

            showSuccess(`User account ${name} updated successfully!`);
        } else {
            submitBtn.innerText = "Registering...";

            await apiFetch("/auth/register", {
                method: "POST",
                body: { name, email, password, role, department_id }
            });

            showSuccess(`User account ${name} registered successfully!`);
        }

        const modalElement = document.getElementById("createUserModal");
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) modalInstance.hide();

        await loadUsersList();

    } catch (err) {
        alert("Operation failed: " + err.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = window.editingUserId ? "Save Changes" : "Register User";
    }
}

async function handleDeleteUser(userId) {
    if (!confirm("Are you sure you want to delete this user account? This action cannot be undone.")) {
        return;
    }

    try {
        await apiFetch(`/auth/users/${userId}`, { method: "DELETE" });
        showSuccess("User account deleted successfully.");
        await loadUsersList();
    } catch (err) {
        alert("Failed to delete user: " + err.message);
    }
}

// -------------------------------------------------------------
// 17. In-App Toast Notifications Banner Renderer
// -------------------------------------------------------------
function showToastNotification(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    
    const toast = document.createElement("div");
    toast.className = `toast align-items-center text-white bg-${type === 'info' ? 'primary' : type} border-0 show shadow`;
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "assertive");
    toast.setAttribute("aria-atomic", "true");
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body small fw-semibold">
                <i class="bi bi-bell-fill me-2"></i> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove toast from DOM after 5 seconds
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}
window.showToastNotification = showToastNotification;

// -------------------------------------------------------------
// 18. Self-Service Profile & Settings Modals
// -------------------------------------------------------------
function openProfileModal() {
    const modalError = document.getElementById("profile-error-alert");
    modalError.classList.add("d-none");
    modalError.innerText = "";
    
    // Pre-fill name field
    document.getElementById("profile-name").value = currentUser.name;
    document.getElementById("profile-old-password").value = "";
    document.getElementById("profile-new-password").value = "";
    
    const modal = new bootstrap.Modal(document.getElementById("profileModal"));
    modal.show();
}
window.openProfileModal = openProfileModal;

async function submitProfileUpdate() {
    const modalError = document.getElementById("profile-error-alert");
    const name = document.getElementById("profile-name").value.trim();
    const oldPassword = document.getElementById("profile-old-password").value;
    const newPassword = document.getElementById("profile-new-password").value;
    
    modalError.classList.add("d-none");
    if (!name) return;
    
    try {
        const res = await apiFetch("/auth/profile", {
            method: "PUT",
            body: {
                name: name,
                old_password: oldPassword || null,
                new_password: newPassword || null
            }
        });
        
        // Update local session
        currentUser.name = res.user.name;
        document.getElementById("user-name-display").innerText = currentUser.name;
        
        // Hide modal
        const modalEl = document.getElementById("profileModal");
        const modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (modalInstance) modalInstance.hide();
        
        showSuccess("Profile settings updated successfully.");
        showToastNotification("Your profile has been updated.", "success");
    } catch (err) {
        modalError.innerText = err.message;
        modalError.classList.remove("d-none");
    }
}
window.submitProfileUpdate = submitProfileUpdate;

// -------------------------------------------------------------
// 19. Departments & Categories Configuration Console (Admin only)
// -------------------------------------------------------------
async function loadAdminSettings() {
    try {
        await Promise.all([
            loadDepartmentsTable(),
            loadCategoriesTable()
        ]);
    } catch (err) {
        showError(err.message);
    }
}
window.loadAdminSettings = loadAdminSettings;

async function loadDepartmentsTable() {
    const tbody = document.getElementById("dept-table-body");
    tbody.innerHTML = '<tr><td colspan="4" class="text-center py-3 text-muted">Loading...</td></tr>';
    
    try {
        const depts = await apiFetch("/admin/departments", { method: "GET" });
        tbody.innerHTML = "";
        
        if (depts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">No departments defined.</td></tr>';
            return;
        }
        
        depts.forEach(d => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${d.id}</strong></td>
                <td>${sanitizeText(d.name)}</td>
                <td class="text-center"><span class="badge bg-secondary">${d.users_count}</span></td>
                <td class="text-end px-3">
                    <button class="btn btn-sm btn-outline-secondary py-0 px-1 me-1" onclick="openEditDeptModal(${d.id}, '${sanitizeText(d.name)}')">
                        <i class="bi bi-pencil-shadow"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger py-0 px-1" onclick="handleDeleteDept(${d.id})">
                        <i class="bi bi-trash"></i> Delete
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-danger py-3">Failed to load: ${err.message}</td></tr>`;
    }
}

let editingDeptId = null;
function openCreateDeptModal() {
    editingDeptId = null;
    document.getElementById("deptModalLabel").innerText = "Add Department";
    document.getElementById("dept-name").value = "";
    document.getElementById("dept-error-alert").classList.add("d-none");
    
    const modal = new bootstrap.Modal(document.getElementById("deptModal"));
    modal.show();
}
window.openCreateDeptModal = openCreateDeptModal;

function openEditDeptModal(id, name) {
    editingDeptId = id;
    document.getElementById("deptModalLabel").innerText = "Edit Department";
    document.getElementById("dept-name").value = name;
    document.getElementById("dept-error-alert").classList.add("d-none");
    
    const modal = new bootstrap.Modal(document.getElementById("deptModal"));
    modal.show();
}
window.openEditDeptModal = openEditDeptModal;

async function submitDepartmentForm() {
    const nameInput = document.getElementById("dept-name");
    const name = nameInput.value.trim();
    const errorAlert = document.getElementById("dept-error-alert");
    
    errorAlert.classList.add("d-none");
    if (!name) return;
    
    try {
        const url = editingDeptId ? `/admin/departments/${editingDeptId}` : "/admin/departments";
        const method = editingDeptId ? "PUT" : "POST";
        
        await apiFetch(url, {
            method: method,
            body: { name: name }
        });
        
        const modalEl = document.getElementById("deptModal");
        const modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (modalInstance) modalInstance.hide();
        
        showSuccess(editingDeptId ? "Department updated successfully." : "Department created successfully.");
        showToastNotification(editingDeptId ? "Department updated." : "Department created.", "success");
        await loadAdminSettings();
    } catch (err) {
        errorAlert.innerText = err.message;
        errorAlert.classList.remove("d-none");
    }
}
window.submitDepartmentForm = submitDepartmentForm;

async function handleDeleteDept(id) {
    if (!confirm("Are you sure you want to delete this department?")) return;
    
    try {
        await apiFetch(`/admin/departments/${id}`, { method: "DELETE" });
        showSuccess("Department deleted successfully.");
        showToastNotification("Department removed.", "success");
        await loadAdminSettings();
    } catch (err) {
        alert("Operation failed: " + err.message);
    }
}
window.handleDeleteDept = handleDeleteDept;

async function loadCategoriesTable() {
    const tbody = document.getElementById("category-table-body");
    tbody.innerHTML = '<tr><td colspan="4" class="text-center py-3 text-muted">Loading...</td></tr>';
    
    try {
        const categories = await apiFetch("/admin/categories", { method: "GET" });
        tbody.innerHTML = "";
        
        if (categories.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">No categories defined.</td></tr>';
            return;
        }
        
        categories.forEach(c => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${sanitizeText(c.name)}</strong></td>
                <td>${sanitizeText(c.department_name)}</td>
                <td class="text-center"><span class="badge bg-secondary">${c.complaints_count}</span></td>
                <td class="text-end px-3">
                    <button class="btn btn-sm btn-outline-secondary py-0 px-1 me-1" onclick="openEditCategoryModal(${c.id}, '${sanitizeText(c.name)}', ${c.department_id})">
                        <i class="bi bi-pencil-shadow"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger py-0 px-1" onclick="handleDeleteCategory(${c.id})">
                        <i class="bi bi-trash"></i> Delete
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-danger py-3">Failed to load: ${err.message}</td></tr>`;
    }
}

let editingCategoryId = null;
async function populateCategoryDeptDropdown(selectedDeptId = null) {
    const select = document.getElementById("category-dept");
    select.innerHTML = '<option value="">-- Choose Department --</option>';
    
    try {
        const depts = await apiFetch("/admin/departments", { method: "GET" });
        depts.forEach(d => {
            const option = document.createElement("option");
            option.value = d.id;
            option.innerText = d.name;
            if (selectedDeptId && d.id === selectedDeptId) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    } catch (err) {
        console.error("Failed to load departments for category form", err);
    }
}

async function openCreateCategoryModal() {
    editingCategoryId = null;
    document.getElementById("categoryModalLabel").innerText = "Add Category";
    document.getElementById("category-name").value = "";
    document.getElementById("category-error-alert").classList.add("d-none");
    
    await populateCategoryDeptDropdown();
    
    const modal = new bootstrap.Modal(document.getElementById("categoryModal"));
    modal.show();
}
window.openCreateCategoryModal = openCreateCategoryModal;

async function openEditCategoryModal(id, name, departmentId) {
    editingCategoryId = id;
    document.getElementById("categoryModalLabel").innerText = "Edit Category";
    document.getElementById("category-name").value = name;
    document.getElementById("category-error-alert").classList.add("d-none");
    
    await populateCategoryDeptDropdown(departmentId);
    
    const modal = new bootstrap.Modal(document.getElementById("categoryModal"));
    modal.show();
}
window.openEditCategoryModal = openEditCategoryModal;

async function submitCategoryForm() {
    const nameInput = document.getElementById("category-name");
    const name = nameInput.value.trim();
    const deptSelect = document.getElementById("category-dept");
    const deptId = deptSelect.value;
    const errorAlert = document.getElementById("category-error-alert");
    
    errorAlert.classList.add("d-none");
    if (!name || !deptId) return;
    
    try {
        const url = editingCategoryId ? `/admin/categories/${editingCategoryId}` : "/admin/categories";
        const method = editingCategoryId ? "PUT" : "POST";
        
        await apiFetch(url, {
            method: method,
            body: { name: name, department_id: deptId }
        });
        
        const modalEl = document.getElementById("categoryModal");
        const modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (modalInstance) modalInstance.hide();
        
        showSuccess(editingCategoryId ? "Category updated successfully." : "Category created successfully.");
        showToastNotification(editingCategoryId ? "Category updated." : "Category created.", "success");
        await loadAdminSettings();
    } catch (err) {
        errorAlert.innerText = err.message;
        errorAlert.classList.remove("d-none");
    }
}
window.submitCategoryForm = submitCategoryForm;

async function handleDeleteCategory(id) {
    if (!confirm("Are you sure you want to delete this category?")) return;
    
    try {
        await apiFetch(`/admin/categories/${id}`, { method: "DELETE" });
        showSuccess("Category deleted successfully.");
        showToastNotification("Category removed.", "success");
        await loadAdminSettings();
    } catch (err) {
        alert("Operation failed: " + err.message);
    }
}
window.handleDeleteCategory = handleDeleteCategory;

