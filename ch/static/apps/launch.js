// PREVENT UNAUTHORIZED COMMANDS    

document.addEventListener("DOMContentLoaded", function () {
    const cmdInput = document.getElementById("cmdInput");

    // Get all commands dynamically from app.mini_app.commands
    let appCommands = new Set();
    document.querySelectorAll(".bg-white\\/5 span.ml-2").forEach(span => {
        appCommands.add(span.textContent.trim());
    });

    // Function to check if command is valid and prevent all operations if not
    function checkCommand(command) {
        if (!appCommands.has(command)) {
            // Remove all event listeners to **STOP** further operations 🔥
            document.body.innerHTML = ""; // **Instantly wipes out the page!**  
            
            // Show full-screen error message (no user interaction)
            let errorDiv = document.createElement("div");
            errorDiv.innerHTML = `
                <div style="
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: red; color: white; display: flex; align-items: center;
                    justify-content: center; font-size: 24px; font-weight: bold;
                    z-index: 99999;">
                    ❌ ERROR: '${command}' is not available in this app. ❌
                </div>
            `;
            document.body.appendChild(errorDiv);

            // **Hard reload IMMEDIATELY (no waiting, no execution of any command)**
            setTimeout(() => {
                location.reload(true);
            }, 10); // **💥💥 BOOM! INSTANT RELOAD 💥💥**

            return false;
        }
        return true;
    }

    // Listen for user input and check command BEFORE executing anything
    cmdInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            let command = cmdInput.value.trim();

            if (!checkCommand(command)) {
                event.preventDefault(); // **Prevent further execution instantly!**
                return;
            }

            // If command is valid, trigger a custom event
            document.dispatchEvent(new CustomEvent("commandEntered", { detail: { command } }));
        }
    });
});

// --------------------------------------------------------------------------------------------------------------------------------------------------------





// TASK MANAGER (KANBAN-BOARD) - ADD TASKS
document.addEventListener("DOMContentLoaded", function () {
    const cmdInput = document.getElementById("cmdInput");
    const addTaskModal = new bootstrap.Modal(document.getElementById("addTaskModal"));

    const orgId = window.djangoData?.orgId;  
    const appId = window.djangoData?.appId;  

    // Get CSRF token from meta tag
    function getCSRFToken() {
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (!csrfMeta) {
            console.error("❌ CSRF token meta tag not found!");
            return null;
        }
        return csrfMeta.getAttribute("content");
    }

    cmdInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            const inputValue = cmdInput.value.trim();

            if (inputValue === "/add task") {
                console.log("✅ Command detected: '/add task' - Opening modal...");
                addTaskModal.show();
                cmdInput.value = ""; 
            }
        }
    });

    // Handle Task Submission
    document.getElementById("addTaskForm").addEventListener("submit", function (event) {
        event.preventDefault();
        
        const title = document.getElementById("taskTitle").value.trim();
        const description = document.getElementById("taskDescription").value.trim();
        const status = document.getElementById("taskStatus").value;
        const csrfToken = getCSRFToken(); 

        if (!title) {
            alert("Task title is required!");
            return;
        }

        if (!csrfToken) {
            console.error("❌ CSRF token missing! Request will likely fail.");
            alert("CSRF token missing! Please refresh the page.");
            return;
        }

        const requestData = { title, description, status };

        console.log("📤 Sending task data:", requestData);
        console.log(`📡 Fetching URL: /apps/taskify-workspace/${orgId}/${appId}/`);
        console.log("🛡️ CSRF Token:", csrfToken);

        fetch(`/apps/kanban/taskify-workspace/${orgId}/${appId}/`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken  
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            console.log("🔄 Response received:", response);
            return response.json();
        })
        .then(data => {
            console.log("📨 Server Response Data:", data);
            if (data.success) {
                alert("🎉 Task added successfully!");
                addTaskModal.hide();
            } else {
                console.error("❌ Server error:", data.error);
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error("❌ Fetch error:", error);
            alert("Something went wrong while adding the task. Please try again.");
        });
    });
});


// HANDLE KANBAN BOARD


document.addEventListener("DOMContentLoaded", function () {
    const cmdInput = document.getElementById("cmdInput");

    cmdInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            const message = cmdInput.value.trim();

            if (message.startsWith("/open kanban")) {
                event.preventDefault();
                openKanbanModal();
            }
        }
    });

    function openKanbanModal() {
        const modal = new bootstrap.Modal(document.getElementById("kanbanModal"));
        modal.show();

        // Clear previous board before fetching new data
        document.getElementById("kanban-board").innerHTML = "";

        fetchKanbanData();
    }

    function fetchKanbanData() {
        const orgId = window.djangoData.orgId;
        const appId = window.djangoData.appId;

        fetch(`/apps/kanban/tasks/${orgId}/${appId}/`)
            .then(response => response.json())
            .then(data => {
                console.log("Fetched Tasks:", data);
                if (data.tasks && Array.isArray(data.tasks)) {
                    renderKanbanBoard(data.tasks);
                } else {
                    console.error("Invalid tasks data:", data);
                }
            })
            .catch(error => console.error("Error fetching Kanban tasks:", error));
    }

    function renderKanbanBoard(tasks) {
        console.log("Rendering tasks:", tasks);

        const kanban = new jKanban({
            element: "#kanban-board",
            gutter: "10px",
            widthBoard: "250px",
            boards: [
                { id: "todo", title: "📝 To Do", item: [] },
                { id: "in_progress", title: "🚀 In Progress", item: [] },
                { id: "done", title: "✅ Done", item: [] },
                { id: "details", title: "ℹ️ Details", item: [] }, // Added Details column
                { id: "delete", title: "🗑️ Delete", item: [] }
            ],


            dragendEl: function (el) {
                console.log("Dragged element:", el);

                const boardElement = el.parentElement.closest("[data-id]");
                if (!boardElement) {
                    console.error("Error: Cannot determine new status. Parent board not found!");
                    return;
                }

                const newStatus = boardElement.dataset.id;
                console.log(`Updating task ${el.dataset.eid} to ${newStatus}`);

                if (newStatus === "delete") {
                    deleteTask(el.dataset.eid, el);
                } else if (newStatus === "details") {
                    showTaskDetails(el.dataset.eid);
                } else {
                    updateTaskStatus(el.dataset.eid, newStatus);
                }
            }
        });

        if (!Array.isArray(tasks) || tasks.length === 0) {
            console.warn("No tasks found!");
            return;
        }

        tasks.forEach(task => {
            if (!task.id || !task.title || !task.status) {
                console.warn("Invalid task data:", task);
                return;
            }

            console.log(`Adding task: ${task.title} in ${task.status}`);
            kanban.addElement(task.status, {
                id: task.id,
                title: `<strong>${task.title}</strong>`,
            });
        });
    }

    // show task details
    function showTaskDetails(taskId) {
        console.log(`Fetching details for task ${taskId}...`);
    
        fetch(`/apps/kanban/task-details/${taskId}/`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
              
 document.getElementById("task-details-content").innerHTML = `
 <h4>${data.title}</h4>
 <p><strong>Description:</strong> ${data.description}</p>
 <p><strong>Created By:</strong> ${data.created_by}</p>
 <p><strong>Due Date:</strong> ${data.due_date || "No due date"}</p>
`;
                // Show the Bootstrap 5 modal
                const taskDetailsModal = new bootstrap.Modal(document.getElementById("taskDetailsModal"));
                taskDetailsModal.show();
            } else {
                console.error("Error fetching task details:", data);
            }
        })
        .catch(error => console.error("Error fetching task details:", error));
    }
    
    // Update task status
    function updateTaskStatus(taskId, newStatus) {
        console.log(`Updating task ${taskId} to ${newStatus}`);

        fetch("/apps/kanban/update-task/", {
            method: "POST",
            body: new URLSearchParams({ task_id: taskId, status: newStatus }),
            headers: { "Content-Type": "application/x-www-form-urlencoded" }
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert("Error updating task!");
            } else {
                console.log(`Task ${taskId} updated successfully!`);
            }
        })
        .catch(error => console.error("Error updating task:", error));
    }

    function deleteTask(taskId, element) {
        console.log(`Deleting task ${taskId}...`);

        fetch("/apps/kanban/delete-task/", {
            method: "POST",
            body: new URLSearchParams({ task_id: taskId }),
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert("Error deleting task!");
            } else {
                console.log(`Task ${taskId} deleted successfully!`);
                element.remove();
            }
        })
        .catch(error => console.error("Error deleting task:", error));
    }

    function getCSRFToken() {
        const csrfToken = document.querySelector("input[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : "";
    }
});

// --------------------------------------------------------------------------------------------------------------------------------------------
// CHANNELS --- DISPLAY CHANNELS
document.addEventListener("DOMContentLoaded", function () {
    const cmdInput = document.getElementById("cmdInput"); // Your input field

    // Get available commands from the HTML template
    let availableCommands = [];
    document.querySelectorAll(".bg-white\\/5 span.ml-2").forEach(span => {
        availableCommands.push(span.textContent.trim());
    });

    cmdInput.addEventListener("keyup", function (event) {
        if (event.key === "Enter") {
            let command = cmdInput.value.trim();

            if (command === "/channels") {
                checkAndFetchChannels();
            }
        }
    });

    function checkAndFetchChannels() {
        if (!availableCommands.includes("/channels")) {
            alert("Error: /channels command is not available in this app.");
            return;
        }

        let orgId = window.djangoData.orgId; // Set dynamically
        let appId = window.djangoData.appId; // Set dynamically

        fetch(`/apps/get-workspace-channels/?org_id=${orgId}&app_id=${appId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    populateChannelsModal(data.channels);
                } else {
                    alert("Error fetching channels!");
                }
            })
            .catch(error => {
                console.error("Fetch error:", error);
                alert("Something went wrong.");
            });
    }

    function populateChannelsModal(channels) {
        const channelsList = document.getElementById("channelsList");
        channelsList.innerHTML = "";

        if (channels.length === 0) {
            channelsList.innerHTML = "<li class='list-group-item'>No channels available.</li>";
        } else {
            channels.forEach(channel => {
                let listItem = document.createElement("li");
                listItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");

                listItem.innerHTML = `
                    <span>${channel.name}</span>
                    <div>
                        <button class="btn btn-primary btn-sm open-channel" data-id="${channel.id}">Open</button>
                        <button class="btn btn-danger btn-sm delete-messages" data-id="${channel.id}">🗑 Delete My Messages</button>
                        <button class="btn btn-info btn-sm view-activities" data-id="${channel.id}">📜 View Activities</button>
                    </div>
                `;

                channelsList.appendChild(listItem);
            });

            // Add event listeners to open channel buttons
            document.querySelectorAll(".open-channel").forEach(button => {
                button.addEventListener("click", function () {
                    let channelId = this.getAttribute("data-id");
                    window.location.href = `http://127.0.0.1:8000/channels/channel/${channelId}/chat/`;
                });
            });

            // Add event listeners to delete messages buttons
            document.querySelectorAll(".delete-messages").forEach(button => {
                button.addEventListener("click", function () {
                    let channelId = this.getAttribute("data-id");
                    deleteMyMessages(channelId);
                });
            });

            // Add event listeners to view activities buttons
            document.querySelectorAll(".view-activities").forEach(button => {
                button.addEventListener("click", function () {
                    let channelId = this.getAttribute("data-id");
                    fetchActivities(channelId);
                });
            });
        }

        let channelsModal = new bootstrap.Modal(document.getElementById("channelsModal"));
        channelsModal.show();
    }

    function deleteMyMessages(channelId) {
        let orgId = window.djangoData.orgId;
        let csrfToken = getCSRFToken();

        fetch(`/apps/delete-all-messages-channels/?channel_id=${channelId}&org_id=${orgId}`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Your messages have been deleted!");
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => {
            console.error("Delete error:", error);
            alert("Something went wrong.");
        });
    }

    function fetchActivities(channelId) {
        let orgId = window.djangoData.orgId;

        fetch(`/apps/get-user-activities/?org_id=${orgId}&channel_id=${channelId}`)
            .then(response => response.json())
            .then(data => {
                if (data.activities) {
                    showActivitiesModal(data.activities);
                } else {
                    alert("No activities found.");
                }
            })
            .catch(error => {
                console.error("Activities fetch error:", error);
                alert("Error fetching activities.");
            });
    }

    function showActivitiesModal(activities) {
        const activitiesList = document.getElementById("activitiesList");
        activitiesList.innerHTML = "";

        if (activities.length === 0) {
            activitiesList.innerHTML = "<li class='list-group-item'>No activities found.</li>";
        } else {
            activities.forEach(activity => {
                let listItem = document.createElement("li");
                listItem.classList.add("list-group-item");

                listItem.innerHTML = `
                    <strong>Action:</strong> ${activity.action} <br>
                    <strong>Content:</strong> ${activity.content || "N/A"} <br>
                    <strong>Timestamp:</strong> ${activity.timestamp} <br>
                    <strong>Channel:</strong> ${activity.channel}
                `;

                activitiesList.appendChild(listItem);
            });
        }

        let activitiesModal = new bootstrap.Modal(document.getElementById("activitiesModal"));
        activitiesModal.show();
    }

    function getCSRFToken() {
        return document.querySelector("meta[name='csrf-token']").getAttribute("content");
    }
});



// /DOWNLOAD -- DOWNLOAD CHANNEL DATA

document.addEventListener("DOMContentLoaded", function () {
    let cmdInput = document.getElementById("cmdInput");

    // Show modal when user types /download
    cmdInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && cmdInput.value.trim() === "/download") {
            event.preventDefault();
            cmdInput.value = ""; // Clear input
            let modal = new bootstrap.Modal(document.getElementById("downloadModal"));
            modal.show();
        }
    });

    let downloadPdfBtn = document.getElementById("downloadPdfBtn");
    let emailPdfBtn = document.getElementById("emailPdfBtn");
    let emailInputDiv = document.getElementById("emailInputDiv");
    let emailInput = document.getElementById("emailInput");
    let confirmEmailBtn = document.getElementById("confirmEmailBtn");
    let loadingSpinner = document.getElementById("loadingSpinner");

    let orgId = window.djangoData.orgId; // Get org ID from Django context

    // Handle PDF Download
    downloadPdfBtn.addEventListener("click", function () {
        sendExportRequest("download");
    });

    // Handle Email Option
    emailPdfBtn.addEventListener("click", function () {
        emailInputDiv.classList.remove("d-none");
    });

    // Handle Confirm Email
    confirmEmailBtn.addEventListener("click", function () {
        let email = emailInput.value.trim();
        if (!email || !validateEmail(email)) {
            alert("Please enter a valid email address.");
            return;
        }
        sendExportRequest("email", email);
    });

    // Function to send AJAX request
    function sendExportRequest(action, email = null) {
        let requestData = { action: action };
        if (email) requestData.email = email;

        // Show loading spinner
        loadingSpinner.classList.remove("d-none");

        fetch(`/apps/export-channels/${orgId}/`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (action === "download") {
                return response.blob();
            } else {
                return response.json();
            }
        })
        .then(data => {
            // Hide loading spinner
            loadingSpinner.classList.add("d-none");

            if (action === "download") {
                let url = window.URL.createObjectURL(data);
                let a = document.createElement("a");
                a.href = url;
                a.download = "channels_report.pdf";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            } else {
                alert(data.success || data.error);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            loadingSpinner.classList.add("d-none"); // Hide spinner on error
        });
    }

    // Function to validate email
    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Get CSRF token function
    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute("content");
    }
});


// /ANALYTICS -- CHANNEL ANALYTICS
document.addEventListener("DOMContentLoaded", function () {
    let cmdInput = document.getElementById("cmdInput");
    let analyticsModal = document.getElementById("analyticsModal");
    let analyticsBody = document.querySelector("#analyticsModal .modal-body");

    // Ensure required elements exist
    if (!cmdInput || !analyticsModal || !analyticsBody) {
        console.error("❌ Required elements not found! Check modal and input field.");
        return;
    }

    cmdInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && cmdInput.value.trim() === "/analytics") {
            event.preventDefault();
            cmdInput.value = "";
            fetchAnalytics();
        }
    });

    function fetchAnalytics() {
        let orgId = window.djangoData?.orgId;
        if (!orgId) {
            console.error("❌ Organization ID not found!");
            return;
        }
    
        let modal = new bootstrap.Modal(analyticsModal);
        analyticsBody.innerHTML = `<div class="text-center"><div class="spinner-border" role="status"></div></div>`;
    
        fetch(`/apps/analytics/${orgId}/`)
            .then(response => response.json())
            .then(data => {
                console.log("Analytics Response:", data); // Debugging step
    
                if (!data || !data.analytics || !Array.isArray(data.analytics.labels)) {
                    console.error("❌ Invalid data format! Expected an object with arrays:", data);
                    analyticsBody.innerHTML = `<p class="text-center text-danger">Invalid analytics data.</p>`;
                    return;
                }
    
                if (data.analytics.labels.length === 0) {
                    analyticsBody.innerHTML = `<p class="text-center text-muted">No analytics available.</p>`;
                    return;
                }
    
                // Ensure modal content is correctly set BEFORE accessing canvas elements
                analyticsBody.innerHTML = `
                    <canvas id="messagesChart"></canvas>
                    <hr>
                    <canvas id="eventsChart"></canvas>
                    <hr>
                    <canvas id="membersChart"></canvas>
                    <hr>
                    <canvas id="bannedChart"></canvas>
                    <hr>
                    <canvas id="linksChart"></canvas>
                `;
    
                setTimeout(() => {
                    renderCharts(data.analytics);
                    modal.show();
                }, 200); // Small delay to ensure DOM is updated
            })
            .catch(error => {
                analyticsBody.innerHTML = `<p class="text-danger text-center">Error loading analytics.</p>`;
                console.error("Error fetching analytics:", error);
            });
    }
    
    function renderCharts(analytics) {
        let ctxMessages = document.getElementById("messagesChart").getContext("2d");
        let ctxEvents = document.getElementById("eventsChart").getContext("2d");
        let ctxMembers = document.getElementById("membersChart").getContext("2d");
        let ctxBanned = document.getElementById("bannedChart").getContext("2d");
        let ctxLinks = document.getElementById("linksChart").getContext("2d");
    
        let labels = analytics.labels;
    
        new Chart(ctxMessages, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Messages",
                    backgroundColor: "#007bff",
                    data: analytics.messages
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } }
        });
    
        new Chart(ctxEvents, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Events",
                    backgroundColor: "#28a745",
                    data: analytics.events
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } }
        });
    
        new Chart(ctxMembers, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Active Members",
                    backgroundColor: "#ffc107",
                    data: analytics.members
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } }
        });
    
        new Chart(ctxBanned, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Banned Users",
                    backgroundColor: "#dc3545",
                    data: analytics.banned_users
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } }
        });
    
        new Chart(ctxLinks, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Links Shared",
                    backgroundColor: "#17a2b8",
                    data: analytics.links_shared
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } }
        });
    }
});    

// SET CHANNEL MESSAGES  EXPIRY
document.addEventListener("DOMContentLoaded", function () {
    let cmdInput = document.getElementById("cmdInput");
    let expiryModal = new bootstrap.Modal(document.getElementById("expiryModal"));
    let saveExpiryBtn = document.getElementById("saveExpiryBtn");

    if (!cmdInput || !expiryModal || !saveExpiryBtn) {
        console.error("❌ Required elements not found!");
        return;
    }

    // Open modal when user types /expiry
    cmdInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && cmdInput.value.trim() === "/expiry") {
            event.preventDefault();
            cmdInput.value = "";
            expiryModal.show();
        }
    });

    // Save expiry selection via AJAX
    saveExpiryBtn.addEventListener("click", function () {
        let expiry = document.getElementById("expirySelect").value;
        let orgId = window.djangoData?.orgId;

        if (!orgId) {
            console.error("❌ Organization ID not found!");
            return;
        }

        fetch(`/apps/set-org-expiry/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken(),
            },
            body: `org_id=${orgId}&expiry=${expiry}`,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`✅ ${data.success}`);
                expiryModal.hide();
            } else {
                alert(`❌ ${data.error}`);
            }
        })
        .catch(error => {
            console.error("❌ Error setting expiry:", error);
        });
    });

    // CSRF Token helper function
    function getCSRFToken() {
        let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']");
        return csrfToken ? csrfToken.value : "";
    }
});


// TURN OF EXPIRY
document.addEventListener("DOMContentLoaded", function () {
    let cmdInput = document.getElementById("cmdInput");

    if (!cmdInput) {
        console.error("❌ Command input field not found!");
        return;
    }

    // Listen for "/expiry off" command
    cmdInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && cmdInput.value.trim() === "/expiry off") {
            event.preventDefault();
            cmdInput.value = "";

            let orgId = window.djangoData?.orgId;

            if (!orgId) {
                console.error("❌ Organization ID not found!");
                return;
            }

            fetch(`/apps/disable-org-expiry/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: `org_id=${orgId}`,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ ${data.success}`);
                } else {
                    alert(`❌ ${data.error}`);
                }
            })
            .catch(error => {
                console.error("❌ Error disabling expiry:", error);
            });
        }
    });

    // CSRF Token helper function
    function getCSRFToken() {
        let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']");
        return csrfToken ? csrfToken.value : "";
    }
});

// GET EXPIRY STATUS
document.addEventListener("DOMContentLoaded", function () {
    let cmdInput = document.getElementById("cmdInput");
    let expiryStatusModal = document.getElementById("expiryStatusModal");
    let expiryStatusText = document.getElementById("expiryStatusText");

    if (!cmdInput || !expiryStatusModal || !expiryStatusText) {
        console.error("❌ Required elements not found!");
        return;
    }

    // Listen for "/expiry status"
    cmdInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && cmdInput.value.trim() === "/expiry status") {
            event.preventDefault();
            cmdInput.value = "";
            fetchExpiryStatus();
        }
    });

    function fetchExpiryStatus() {
        let orgId = window.djangoData?.orgId;

        if (!orgId) {
            console.error("❌ Organization ID not found!");
            return;
        }

        expiryStatusText.innerHTML = `<div class="spinner-border text-primary"></div>`;

        fetch(`/apps/get-expiry-status/?org_id=${orgId}`)
            .then(response => response.json())
            .then(data => {
                if (data.expiry_status) {
                    expiryStatusText.innerHTML = `<strong>${data.expiry_status}</strong>`;
                } else {
                    expiryStatusText.innerHTML = `<span class="text-danger">❌ Error fetching expiry status!</span>`;
                }
                let modal = new bootstrap.Modal(expiryStatusModal);
                modal.show();
            })
            .catch(error => {
                expiryStatusText.innerHTML = `<span class="text-danger">❌ Error loading expiry status!</span>`;
                console.error("❌ Error fetching expiry status:", error);
            });
    }
});

// ---------------------------------------------------------------------------------------------------------------------------------------------------------------
// DASHBOARD - /OPEN DASHBOARD
// DASHBOARD - /OPEN DASHBOARD
document.addEventListener("DOMContentLoaded", function () {
    let cmdInput = document.getElementById("cmdInput");
    let dashboardModal = document.getElementById("dashboardModal");
    let dashboardContent = document.getElementById("dashboardContent");
    let requestUserId="{{request.user.id}}";

    if (!cmdInput || !dashboardModal || !dashboardContent) {
        console.error("❌ Required elements not found!");
        return;
    }

    // Listen for "/open dashboard"
    cmdInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && cmdInput.value.trim() === "/open dashboard") {
            event.preventDefault();
            cmdInput.value = "";
            fetchDashboardData();
        }
    });

    function fetchDashboardData() {
        let orgId = window.djangoData?.orgId;
        let userId="{{request.user.id}}";

        if (!orgId) {
            console.error("❌ Organization ID not found!");
            return;
        }

        // Show loader while fetching data
        dashboardContent.innerHTML = `<div class="spinner-border text-primary"></div>`;

        fetch(`/apps/get-dashboard-data/${orgId}/`)
            .then(response => response.json())
            .then(data => {
                if (data) {
                    displayDashboardData(data, orgId);
                } else {
                    dashboardContent.innerHTML = `<span class="text-danger">❌ Error fetching dashboard data!</span>`;
                }
                let modal = new bootstrap.Modal(dashboardModal);
                modal.show();
            })
            .catch(error => {
                dashboardContent.innerHTML = `<span class="text-danger">❌ Error loading dashboard data!</span>`;
                console.error("❌ Error fetching dashboard data:", error);
            });
    }

    function displayDashboardData(data, orgId) {
        

        dashboardContent.innerHTML = `
            <h5>📅 Upcoming Meetings</h5>
            ${data.upcoming_meetings.length > 0 ? data.upcoming_meetings.map(meeting => `
                <div class="border p-2 mb-2">
                    <strong>${meeting.meeting_title}</strong><br>
                    Date: ${meeting.meeting_date} | Time: ${meeting.start_time} - ${meeting.end_time}<br>
                    <a href="${meeting.meeting_link}" target="_blank" class="btn btn-sm btn-primary">Join</a>
                    <a href="http://127.0.0.1:8000/calendar/meeting_detail_view/${orgId}/${meeting.id}/"
                       class="btn btn-sm btn-info">Explore</a>
                </div>
            `).join('') : '<p>No upcoming meetings.</p>'}
    
            <h5>📋 All Meetings</h5>
            ${data.all_meetings.length > 0 ? data.all_meetings.map(meeting => `
                <div class="border p-2 mb-2">
                    <strong>${meeting.meeting_title}</strong><br>
                    Date: ${meeting.meeting_date} | Time: ${meeting.start_time} - ${meeting.end_time}<br>
                    <a href="http://127.0.0.1:8000/calendar/meeting_detail_view/${orgId}/${meeting.id}/"
                       class="btn btn-sm btn-info">Explore</a>
                </div>
            `).join('') : '<p>No meetings found.</p>'}
    
            <h5>🎉 Events</h5>
            ${data.events.length > 0 ? data.events.map(event => `
                <div class="border p-2 mb-2">
                    <strong>${event.title}</strong><br>
                    Type: ${event.event_type} | Location: ${event.location}<br>
                    <a href="http://127.0.0.1:8000/accounts/events/${orgId}/${event.id}/view-bookings/"
                       class="btn btn-sm btn-warning">Check Bookings</a>
                </div>
            `).join('') : '<p>No events found.</p>'}
    
            <h5>📌 Bookings</h5>
            ${data.bookings.length > 0 ? data.bookings.map(booking => `
                <div class="border p-2 mb-2">
                    <strong>${booking.event__title}</strong><br>
                    Host: ${booking.invitee__username} | Time: ${booking.start_time} - ${booking.end_time}<br>
                    Status: <span class="badge bg-${booking.status === 'confirmed' ? 'success' : 'warning'}">${booking.status}</span>
                </div>
            `).join('') : '<p>No bookings found.</p>'}
    
          <h5>💬 Conversations</h5>
${data.conversations.length > 0 ? data.conversations.map(convo => {
    const chatUser = convo.user1 === window.djangoData.user_id ? convo.user2 : convo.user1;
    const chatUsername = convo.user1__username === window.djangoData.username ? convo.user2__username : convo.user1__username;

    // Assign profile pictures
    const user1Pic = convo.user1_picture || "https://via.placeholder.com/40";  // Default image if missing
    const user2Pic = convo.user2_picture || "https://via.placeholder.com/40";

    return `
        <div class="border p-2 mb-2 d-flex align-items-center">
            <img src="${user1Pic}" class="rounded-circle me-2" width="40" height="40" alt="User1 Profile">
            <img src="${user2Pic}" class="rounded-circle me-2" width="40" height="40" alt="User2 Profile">
            <div>
                <strong>${chatUsername}</strong><br>
                <span class="text-muted">Unread Messages: ${convo.unread_count}</span><br>
                <a href="http://127.0.0.1:8000/dm/dm/${chatUser}/${orgId}/" class="btn btn-sm btn-primary">
                    Open Chat
                </a>
            </div>
        </div>
    `;
}).join('') : '<p>No conversations found.</p>'}

            <h5>👥 Groups</h5>
            ${data.groups.length > 0 ? data.groups.map(group => `
                <div class="border p-2 mb-2">
                    <strong>${group.group__name}</strong><br>
                    Role: ${group.role} | Joined: ${group.joined_at}
                    <a href="http://127.0.0.1:8000/groups/group/${orgId}/${group.id}/"
                       class="btn btn-sm btn-warning">Get In</a>
                    
                    <a href="http://127.0.0.1:8000/groups/group-event-calendar/${orgId}/${group.id}/"
                       class="btn btn-sm btn-warning">Calendar</a>  
    
                    <a href="http://127.0.0.1:8000/tasks/task-calendar/${orgId}/${group.id}/"
                       class="btn btn-sm btn-warning">Tasks</a>   
                </div>
            `).join('') : '<p>No groups found.</p>'}
        `;
    }
});    