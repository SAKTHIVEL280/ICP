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
            
            // Managers get assignment shortcuts
            if (role === "Manager") {
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
        // Fetch active technicians list in the manager's department
        const technicians = await apiFetch("/manager/technicians", { method: "GET" });
        
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
async function loadNotifications() {
    try {
        const list = await apiFetch("/notifications", { method: "GET" });
        const unreadCount = list.filter(n => !n.is_read).length;

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
            a.className = `dropdown-item ${n.is_read ? '' : 'fw-bold'}`;
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
    tableBody.innerHTML = '<tr><td colspan="7" class="text-center">Loading user records...</td></tr>';
    
    try {
        // Fetch accounts list from secure backend endpoint
        const users = await apiFetch("/auth/users", { method: "GET" });
        tableBody.innerHTML = "";

        if (users.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">No users registered in your scope.</td></tr>`;
            return;
        }

        // Render rows
        users.forEach(u => {
            const row = document.createElement("tr");
            
            // Format status badge
            const statusBadge = u.is_active 
                ? '<span class="badge bg-success">Active</span>' 
                : '<span class="badge bg-secondary">Inactive</span>';

            row.innerHTML = `
                <td>${u.id}</td>
                <td><strong>${sanitizeText(u.employee_id)}</strong></td>
                <td>${sanitizeText(u.name)}</td>
                <td>${sanitizeText(u.email)}</td>
                <td><span class="badge bg-primary">${sanitizeText(u.role)}</span></td>
                <td>${sanitizeText(u.department_name)}</td>
                <td>${statusBadge}</td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        showError("Failed to load user accounts: " + err.message);
    }
}

async function openCreateUserModal() {
    // Reset any previous form fields
    const form = document.getElementById("create-user-form");
    form.reset();

    const role = currentUser.role;
    const deptGroup = document.getElementById("usr-dept-group");
    const deptSelect = document.getElementById("usr-dept");
    const roleSelect = document.getElementById("usr-role");

    try {
        // Populate departments select menu from categories list
        const categories = await apiFetch("/complaints/categories", { method: "GET" });
        deptSelect.innerHTML = '<option value="">-- Choose Department --</option>';
        
        // Filter unique departments
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

        // Apply view adjustments based on role permissions
        if (role === "Manager") {
            // Managers are restricted to their own department, so hide input selection
            deptGroup.classList.add("d-none");
            deptSelect.removeAttribute("required");

            // Managers can only create Employee and Technician roles
            roleSelect.innerHTML = `
                <option value="Employee">Employee</option>
                <option value="Technician">Technician</option>
            `;
        } else if (role === "Administrator") {
            // Administrators must specify a department and can assign all roles
            deptGroup.classList.remove("d-none");
            deptSelect.setAttribute("required", "required");

            roleSelect.innerHTML = `
                <option value="Employee">Employee</option>
                <option value="Technician">Technician</option>
                <option value="Manager">Manager</option>
                <option value="Administrator">Administrator</option>
            `;
        }

        // Show modal Dialog
        const modal = new bootstrap.Modal(document.getElementById("createUserModal"));
        modal.show();

    } catch (err) {
        showError("Failed to initialize registration form: " + err.message);
    }
}

async function handleUserCreateSubmit(e) {
    e.preventDefault();

    const employee_id = document.getElementById("usr-emp-id").value;
    const name = document.getElementById("usr-name").value;
    const email = document.getElementById("usr-email").value;
    const password = document.getElementById("usr-password").value;
    const role = document.getElementById("usr-role").value;
    
    // Only fetch department if Administrator (Managers department is resolved by backend)
    const deptSelect = document.getElementById("usr-dept");
    const department_id = (currentUser.role === "Administrator" && deptSelect.value) 
        ? parseInt(deptSelect.value) 
        : null;

    const submitBtn = document.getElementById("usr-submit-btn");

    try {
        submitBtn.disabled = true;
        submitBtn.innerText = "Registering...";

        // Submit to registration API endpoint
        await apiFetch("/auth/register", {
            method: "POST",
            body: {
                employee_id,
                name,
                email,
                password,
                role,
                department_id
            }
        });

        // Hide registration modal dialog
        const modalElement = document.getElementById("createUserModal");
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) modalInstance.hide();

        showSuccess(`User account ${name} registered successfully!`);
        
        // Reload users list data
        await loadUsersList();

    } catch (err) {
        alert("Registration failed: " + err.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = "Register User";
    }
}
