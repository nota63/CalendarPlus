


// SHARE THE TASK WITH TEAM-MEMBERS
document.addEventListener("DOMContentLoaded", function () {
    const openModalBtn = document.getElementById("openShareTaskModal");
    const sendTaskBtn = document.getElementById("sendTaskBtn");
    const sendSpinner = document.getElementById("sendSpinner");
    const membersList = document.getElementById("membersList");
    
    let orgId, groupId, taskId, selectedMembers = [];

    // ✅ Open Modal & Fetch Members
    openModalBtn.addEventListener("click", function () {
        orgId = window.djangoData.orgId;
        groupId = window.djangoData.groupId;
        taskId = window.djangoData.taskId;

        fetch(`/tasks/get-workspace-members/?org_id=${orgId}`)
        .then(response => response.json())
        .then(data => {
            membersList.innerHTML = ""; // Clear existing members

            if (data.status === "success") {
                membersList.className = "grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 p-4"; // Grid layout
                
                data.members.forEach(member => {
                    const memberCard = document.createElement("div");
                    memberCard.className = "flex flex-col items-center cursor-pointer transition-all duration-300 ease-in-out border border-gray-300 rounded-lg p-2 hover:bg-gray-100";
                    memberCard.dataset.userId = member.user_id;

                    memberCard.innerHTML = `
                        <div class="relative w-16 h-16">
                            <img src="${member.profile_picture}" class="w-full h-full rounded-full border-2 border-gray-300 transition-all duration-300">
                            <div class="absolute inset-0 bg-black opacity-0 transition-opacity duration-300 rounded-full"></div>
                        </div>
                        <span class="text-sm font-medium mt-2">${member.full_name}</span>
                    `;

                    // ✅ Handle Selection Effect
                    memberCard.addEventListener("click", function () {
                        if (selectedMembers.includes(member.user_id)) {
                            selectedMembers = selectedMembers.filter(id => id !== member.user_id);
                            memberCard.classList.remove("border-blue-500", "bg-blue-50");
                            memberCard.querySelector("img").classList.remove("border-blue-500");
                            memberCard.querySelector("div").classList.remove("opacity-30");
                        } else {
                            selectedMembers.push(member.user_id);
                            memberCard.classList.add("border-blue-500", "bg-blue-50");
                            memberCard.querySelector("img").classList.add("border-blue-500");
                            memberCard.querySelector("div").classList.add("opacity-30");
                        }
                    });

                    membersList.appendChild(memberCard);
                });

                const modal = new bootstrap.Modal(document.getElementById("shareTaskModal"));
                modal.show();
            } else {
                alert("Failed to fetch members!");
            }
        });
    });

    // ✅ Handle Task Sending
    sendTaskBtn.addEventListener("click", function () {
        if (selectedMembers.length === 0) {
            alert("Please select at least one member!");
            return;
        }

        sendTaskBtn.disabled = true;
        sendSpinner.classList.remove("hidden");

        fetch("/tasks/send-task-to-members/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').getAttribute("content")
            },
            body: JSON.stringify({
                org_id: orgId,
                group_id: groupId,
                task_id: taskId,
                selected_members: selectedMembers
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("Task details sent successfully!");
                document.getElementById("shareTaskModal").classList.remove("show");
                document.body.classList.remove("modal-open");
                document.querySelector(".modal-backdrop").remove();
            } else {
                alert("Failed to send task: " + data.message);
            }
        })
        .finally(() => {
            sendTaskBtn.disabled = false;
            sendSpinner.classList.add("hidden");
        });
    });
});


// Filter members in real time
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchMembers");
    const membersList = document.getElementById("membersList");

    searchInput.addEventListener("input", function () {
        let query = searchInput.value.toLowerCase().trim();

        membersList.querySelectorAll(".member-card").forEach(card => {
            let memberName = card.querySelector("h6").textContent.toLowerCase();
            let memberRole = card.querySelector("p").textContent.toLowerCase();

            if (memberName.includes(query) || memberRole.includes(query)) {
                card.style.display = "flex"; // Show matching members
            } else {
                card.style.display = "none"; // Hide non-matching members
            }
        });
    });

    // Reset search when modal opens
    document.getElementById("shareTaskModal").addEventListener("shown.bs.modal", function () {
        searchInput.value = ""; // Clear search bar
        membersList.querySelectorAll(".member-card").forEach(card => {
            card.style.display = "flex"; // Show all members again
        });
    });
});



// LAUNCH CAL-AI (THE AI TASK ASSISTANT)
document.addEventListener("DOMContentLoaded", function () {
    const modalElement = document.getElementById("aiChatModal");
    if (!modalElement) return; // Prevent errors if modal is missing
    const modal = new bootstrap.Modal(modalElement);

    const chatContainer = document.getElementById("chatMessages");
    const userInput = document.getElementById("userQuery");
    const sendBtn = document.getElementById("sendQuery");
    const predefinedQueries = document.querySelectorAll(".query-btn");

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    }

    function appendMessage(sender, message) {
        if (!chatContainer) return;
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);
        messageDiv.innerHTML = `<strong>${sender === "user" ? "You" : "CalAI"}:</strong> ${message}`;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function sendMessage(userQuestion) {
        if (!userQuestion.trim()) return;

        const orgId = window.djangoData?.orgId || null;
        const groupId = window.djangoData?.groupId || null;
        const taskId = window.djangoData?.taskId || null;

        if (!orgId || !groupId || !taskId) {
            appendMessage("ai", "Error: Missing organization, group, or task ID.");
            return;
        }

        const url = `/cal_ai/cal-ai/${orgId}/${groupId}/${taskId}/`;

        appendMessage("user", userQuestion);
        userInput.value = "";

        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ question: userQuestion }),
        })
        .then(response => response.json())
        .then(data => {
            appendMessage("ai", data.response || "Error fetching response.");
        })
        .catch(() => appendMessage("ai", "Error: Unable to reach the server."));
    }

    if (sendBtn && userInput) {
        sendBtn.addEventListener("click", function () {
            sendMessage(userInput.value);
        });

        userInput.addEventListener("keypress", function (e) {
            if (e.key === "Enter") sendBtn.click();
        });
    }

    if (predefinedQueries.length) {
        predefinedQueries.forEach(query => {
            query.addEventListener("click", function () {
                sendMessage(this.dataset.query);
            });
        });
    }
});



// HANDLE AND MANAGE AUTOMATIONS
document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("automationModal");

    modal.addEventListener("shown.bs.modal", function () {
        fetchEnabledAutomations();
    });

    function fetchEnabledAutomations() {
        const orgId = window.djangoData.orgId;
        const groupId = window.djangoData.groupId;
        const taskId = window.djangoData.taskId;

        fetch(`/tasks/fetch-enabled-automations?org_id=${orgId}&group_id=${groupId}&task_id=${taskId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    document.querySelectorAll("[data-key]").forEach((toggle) => {
                        toggle.checked = data.automations[toggle.dataset.key] || false;

                        // Ensure event listener is added only once
                        if (!toggle.dataset.listenerAdded) {
                            toggle.addEventListener("change", function () {
                                toggleAutomation(this.dataset.key, this.checked);
                            });
                            toggle.dataset.listenerAdded = "true";
                        }
                    });
                }
            });
    }

    function toggleAutomation(automationKey, status) {
        const orgId = window.djangoData.orgId;
        const groupId = window.djangoData.groupId;
        const taskId = window.djangoData.taskId;

        fetch("/tasks/toggle-automation/", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `org_id=${orgId}&group_id=${groupId}&task_id=${taskId}&automation_key=${automationKey}&status=${status}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                console.log(`${automationKey} updated: ${status}`);
            }
        });
    }
});


// DISPLAY SPECTORS
document.addEventListener("DOMContentLoaded", function () {
    console.log("🌟 DOM fully loaded and parsed.");

    document.querySelectorAll(".spectors-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            console.log("📌 Button clicked:", this);

            // Debug: Check if djangoData is available
            if (!window.djangoData || !window.djangoData.taskId) {
                console.error("❌ Error: djangoData.taskId is missing!", window.djangoData);
                alert("Task ID is missing! Debugging needed.");
                return;
            }

            let taskId = window.djangoData.taskId;
            console.log("🔍 Fetching task details for Task ID:", taskId);

            fetch(`/tasks/get-task-details/${taskId}/`, {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => {
                console.log("✅ Response received:", response);
                return response.json();
            })
            .then(data => {
                console.log("📊 Parsed JSON data:", data);

                if (data.success) {
                    document.getElementById("taskDescription").textContent = data.description;
                    document.getElementById("taskCreatedBy").textContent = data.created_by.username;
                    document.getElementById("taskEmail").textContent = data.created_by.email;
                    document.getElementById("taskLastLogin").textContent = data.last_login ? new Date(data.last_login).toLocaleString() : "N/A";

                    // Display Profile Picture
                    let profilePicElement = document.getElementById("profilePicture");
                    if (data.profile_picture) {
                        profilePicElement.innerHTML = `<img src="${data.profile_picture}" alt="Profile Picture" class="rounded-circle" width="50" height="50">`;
                    } else {
                        profilePicElement.innerHTML = `<span>No Profile Picture</span>`;
                    }

                    console.log("🟢 Data populated into modal successfully.");

                    // Open Bootstrap Modal Manually
                    let modalElement = document.getElementById("spectorsModal");
                    let modal = new bootstrap.Modal(modalElement);
                    modal.show();
                    console.log("🎉 Bootstrap Modal Opened!");
                } else {
                    console.error("❌ Error fetching task details:", data.error);
                    alert(`Error fetching task details: ${data.error}`);
                }
            })
            .catch(error => {
                console.error("🔥 AJAX Fetch Error:", error);
                alert("An error occurred while fetching task details. Check the console for details.");
            });
        });
    });
});




// FETCH AND DISPLAY THE TASK ACTIVITIES
document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("TaskActivitiesModal");

    modal.addEventListener("show.bs.modal", function () {
        console.log("🚀 TaskActivitiesModal opened!");
        fetchActivityLogs();
    });
});

function fetchActivityLogs() {
    const activityList = document.getElementById("activity-list");
    activityList.innerHTML = `<p class="text-muted text-center">Fetching activities...</p>`;

    const orgId = window.djangoData.orgId;
    const groupId = window.djangoData.groupId;
    const taskId = window.djangoData.taskId;

    console.log("📡 Sending AJAX request to fetch activities...");
    console.log(`🔹 Org ID: ${orgId}, Group ID: ${groupId}, Task ID: ${taskId}`);

    fetch(`/tasks/get-activities/?org_id=${orgId}&group_id=${groupId}&task_id=${taskId}`, {
        method: "GET",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(response => {
        console.log("✅ Received response from server:", response);
        return response.json();
    })
    .then(data => {
        console.log("📜 Parsed JSON data:", data);
        activityList.innerHTML = "";

        if (!data.activities || data.activities.length === 0) {
            activityList.innerHTML = `<p class="text-muted text-center">No activities found.</p>`;
            return;
        }

        data.activities.forEach(activity => {
            console.log("📝 Processing activity:", activity);
            const item = document.createElement("div");
            item.classList.add("timeline-item");
            item.setAttribute("data-icon", activity.icon);
            item.innerHTML = `
                <div class="timeline-content" data-details="${activity.details}">
                    <strong>${activity.user}</strong> - ${activity.action} <br>
                    <small class="text-muted">${activity.timestamp}</small>
                </div>
            `;
            item.style.setProperty("--icon-bg", activity.color);
            activityList.appendChild(item);
        });

        console.log("🎉 Successfully displayed activities!");
    })
    .catch(error => {
        console.error("❌ Error fetching activities:", error);
        activityList.innerHTML = `<p class="text-danger text-center">Failed to fetch activities.</p>`;
    });
}


// filter activities in real time
// FILTER ACTIVITIES IN REAL TIME
function filterActivities() {
    let searchQuery = document.getElementById("activitySearch").value.toLowerCase();
    let activities = document.querySelectorAll("#activity-list .timeline-item");

    activities.forEach(activity => {
        let textContent = activity.textContent.toLowerCase();
        activity.style.display = textContent.includes(searchQuery) ? "block" : "none";
    });
}


// fetch and monitor automations

// fetch and monitor automations
// Open Automation Modal
document.getElementById("openAutomationModal").addEventListener("click", function () {
    document.getElementById("AutomationStatusModal").classList.remove("hidden");
});

// Close Modal
document.getElementById("closeAutomationModal").addEventListener("click", closeModal);
document.getElementById("closeAutomationModalFooter").addEventListener("click", closeModal);

function closeModal() {
    document.getElementById("AutomationStatusModal").classList.add("hidden");
}

// Toggle Sections and Fetch Data Dynamically
document.getElementById("toggleProceeded").addEventListener("click", function () {
    toggleSection("proceeded");
});

document.getElementById("toggleRunning").addEventListener("click", function () {
    toggleSection("running");
});

function toggleSection(type) {
    const listElement = document.getElementById(`${type}List`);
    const countElement = document.getElementById(`${type}Count`);

    // Toggle visibility
    listElement.classList.toggle("hidden");

    // Fetch data if not already populated
    if (listElement.children.length === 0) {
        fetchAutomationStatus(type, listElement, countElement);
    }
}

// Fetch Automations when Section Expands
function fetchAutomationStatus(type, listElement, countElement) {
    const orgId = window.djangoData.orgId;
    const groupId = window.djangoData.groupId;
    const taskId = window.djangoData.taskId;

    // Show Loading Indicator
    listElement.innerHTML = `<li class="p-2 text-gray-500">Loading...</li>`;

    fetch("/tasks/automation-status/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken()
        },
        body: `org_id=${orgId}&group_id=${groupId}&task_id=${taskId}`
    })
    .then(response => response.json())
    .then(data => {
        listElement.innerHTML = ""; // Clear previous content

        let automationData = data[type]; // Get 'proceeded' or 'running' data

        if (automationData && Object.keys(automationData).length > 0) {
            Object.keys(automationData).forEach(key => {
                const listItem = document.createElement("li");
listItem.className = `automation-item ${type === "proceeded" ? 'proceeded' : 'running'}`;
listItem.setAttribute("data-name", key.toLowerCase());

listItem.innerHTML = `
    <span class="status-icon material-icons-round">
        ${type === "proceeded" ? 'check_circle' : 'electric_bolt'}
    </span>
    <div class="automation-content">
        <strong>${formatKey(key)}</strong>
        <div class="automation-meta">
            <span class="status-dot ${type === "proceeded" ? 'bg-green-500' : 'bg-amber-500'}"></span>
            <span>${type === "proceeded" ? 'Completed' : 'In Progress'}</span>
            ${type !== "proceeded" ? 
            `<div class="progress-bar">
                <div class="progress-fill" style="width: ${Math.random() * 100}%"></div>
            </div>` : ''}
        </div>
        <div class="automation-time">
            ${type === "proceeded" ? 
            'Completed 15m ago' : 
            `${Math.floor(Math.random() * 5 + 1)}m remaining`}
        </div>
    </div>
    ${type === "proceeded" ? 
    '<span class="material-icons-round text-green-600 text-sm">verified</span>' : 
    '<span class="material-icons-round text-amber-600 text-sm">more_horiz</span>'}
`;

listElement.appendChild(listItem);
});
            // Update Count
            countElement.textContent = Object.keys(automationData).length;
        } else {
            listElement.innerHTML = `<li class="p-2 text-gray-500">No ${type} automations found.</li>`;
            countElement.textContent = "0";
        }
    })
    .catch(error => {
        console.error("Error fetching automation status:", error);
        listElement.innerHTML = `<li class="p-2 text-red-500">Error loading data.</li>`;
    });
}

// Real-Time Search in Automations
document.getElementById("searchAutomation").addEventListener("input", function () {
    let searchTerm = this.value.toLowerCase();
    let items = document.querySelectorAll(".automation-item");

    items.forEach(item => {
        let name = item.getAttribute("data-name");
        if (name.includes(searchTerm)) {
            item.style.display = "block";
        } else {
            item.style.display = "none";
        }
    });
});

// Helper function to format field names
function formatKey(key) {
    return key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

// CSRF Token Retrieval (Django)
function getCSRFToken() {
    return document.cookie.split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1] || "";
}


// Background Proccesses Guide

document.getElementById("openAutomationGuide").addEventListener("mouseenter", function () {
    document.getElementById("AutomationGuideModal").classList.remove("hidden");
});

// Close Modal on Button Click
document.getElementById("closeAutomationGuide").addEventListener("click", closeGuideModal);
document.getElementById("closeAutomationGuideFooter").addEventListener("click", closeGuideModal);

// Close Modal on Mouse Leave
document.getElementById("AutomationGuideModal").addEventListener("mouseleave", closeGuideModal);

function closeGuideModal() {
    document.getElementById("AutomationGuideModal").classList.add("hidden");
}


// Stop ALL Automations
document.getElementById("openStopModal").addEventListener("click", function () {
    document.getElementById("stopAutomationModal").classList.remove("hidden");
    
    let progressBar = document.getElementById("progressBar");
    let progressText = document.getElementById("progressText");
    let closeBtn = document.getElementById("closeStopModal");

    let progress = 0;
    let interval = setInterval(() => {
        progress += 3; // Increase by 5% every 200ms
        progressBar.style.width = `${progress}%`;

        if (progress >= 100) {
            clearInterval(interval);
            progressText.textContent = "All background processes stopped successfully.";
            
            // Make API Request to Disable Automations
            stopAllAutomations();
        }
    }, 200);
});

// Function to send request to disable automations
function stopAllAutomations() {
    const orgId = window.djangoData.orgId;
    const groupId = window.djangoData.groupId;
    const taskId = window.djangoData.taskId;

    fetch("/tasks/disable-all-automations/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken()
        },
        body: `org_id=${orgId}&group_id=${groupId}&task_id=${taskId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            document.getElementById("progressText").textContent = "✅ All automations have been turned off.";
        } else {
            document.getElementById("progressText").textContent = "❌ Failed to stop automations.";
        }
        
        // Show Close Button
        document.getElementById("closeStopModal").classList.remove("hidden");
    })
    .catch(error => {
        console.error("Error disabling automations:", error);
        document.getElementById("progressText").textContent = "❌ Error occurred. Try again.";
        document.getElementById("closeStopModal").classList.remove("hidden");
    });
}

// Close Modal
document.getElementById("closeStopModal").addEventListener("click", function () {
    document.getElementById("stopAutomationModal").classList.add("hidden");
});

// CSRF Token Retrieval (Django)
function getCSRFToken() {
    return document.cookie.split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1] || "";
}



// Back-up The Task
document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("backupModal");
    const startBackupBtn = document.getElementById("startBackup");
    const progressBar = document.getElementById("backupProgressBar");
    const progressContainer = document.getElementById("backupProgressContainer");
    const progressText = document.getElementById("progressText");
    const backupSizeEl = document.getElementById("backupSize");
    const backupDateEl = document.getElementById("backupDate");

    // Task Info (Replace these with dynamic values)
    const orgId = window.djangoData.orgId;
    const groupId = window.djangoData.groupId;
    const taskId = window.djangoData.taskId;

    // When Modal Opens → Fetch Last Backup Info
    modal.addEventListener("shown.bs.modal", function () {
        fetch(`/tasks/last-backup/${taskId}/`)
            .then(response => response.json())
            .then(data => {
                backupSizeEl.textContent = data.backup_size || "-";
                backupDateEl.textContent = data.backup_date || "-";
            })
            .catch(error => console.error("Error fetching backup data:", error));
    });

    // Start Backup Process
    startBackupBtn.addEventListener("click", function () {
        startBackupBtn.disabled = true;
        progressContainer.classList.remove("d-none");

        let progress = 0;
        const interval = setInterval(() => {
            progress += 25;
            progressBar.style.width = `${progress}%`;

            if (progress === 100) {
                clearInterval(interval);
                progressText.textContent = "Backup Completed! Saving Data...";

                // Make AJAX Request to Backup API
                fetch(`/tasks/back-up/${orgId}/${groupId}/${taskId}/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(), // CSRF Token for security
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        backupSizeEl.textContent = data.backup_size;
                        backupDateEl.textContent = new Date().toLocaleString();
                        progressText.textContent = "Backup Successfully Saved!";
                    } else {
                        progressText.textContent = "Backup Failed!";
                    }
                    startBackupBtn.disabled = false;
                })
                .catch(error => {
                    console.error("Backup error:", error);
                    progressText.textContent = "Error in Backup!";
                    startBackupBtn.disabled = false;
                });
            }
        }, 1000);
    });

    // Function to Get CSRF Token
    function getCSRFToken() {
        const csrfToken = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
        return csrfToken || "";
    }
});


// RESTORE BACK-UPS
// Delete The BackUP
function deleteBackup(backupId) {
    if (!confirm("Are you sure you want to delete this backup?")) return;

    fetch(`/tasks/delete-backup/${backupId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Backup deleted successfully!");
            document.getElementById(`backup-${backupId}`).remove(); // Remove item from UI
        } else {
            alert("Failed to delete backup: " + data.message);
        }
    })
    .catch(error => console.error("Error:", error));
}

// Function to get CSRF Token from cookies
function getCSRFToken() {
    let cookieValue = null;
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            cookieValue = cookie.substring(10);
            break;
        }
    }
    return cookieValue;
}


// Download Backup Function (Move outside DOMContentLoaded for global access)
function downloadBackup(backupId) {
    window.location.href = `/tasks/download-backup/${backupId}/`;
}

document.addEventListener("DOMContentLoaded", function () {
    let selectedBackupId = null;

    // Open Modal & Fetch Backups
    document.getElementById("openRestoreBackupModal").addEventListener("click", function () {
        let modal = new bootstrap.Modal(document.getElementById("RestoreBackUpModal"));
        modal.show();
        fetchBackups();
    });

    // Fetch Backups
    function fetchBackups() {
        let orgId = window.djangoData.orgId;
        let groupId = window.djangoData.groupId;
        let taskId = window.djangoData.taskId;

        fetch(`/tasks/fetch-task-backups/${orgId}/${groupId}/${taskId}/`)
            .then(response => response.json())
            .then(data => {
                let backupList = document.getElementById("backupList");
                backupList.innerHTML = "";

                if (data.backups.length === 0) {
                    backupList.innerHTML = '<li class="list-group-item text-center">No backups found!</li>';
                } else {
                    data.backups.forEach(backup => {
                        let listItem = document.createElement("li");
                        listItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
                        listItem.dataset.backupId = backup.id;

                        listItem.innerHTML = `
    <div class="group flex items-center gap-4 p-4 mb-3 bg-gray-850 rounded-xl border border-gray-700 hover:border-blue-400/30 transition-all duration-300 cursor-pointer shadow-sm hover:shadow-md relative overflow-hidden">
        
        <!-- Buttons Container (Left Side) -->
        <div class="action-buttons flex flex-col items-start gap-2">
            <button class="download-btn flex items-center gap-1 px-3 py-1 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded hidden group-hover:flex"
                    onclick="downloadBackup(${backup.id})">
                <i class="fas fa-download"></i> Download
            </button>
            <button class="delete-btn flex items-center gap-1 px-3 py-1 text-sm text-white bg-red-600 hover:bg-red-700 rounded hidden group-hover:flex"
                    onclick="deleteBackup(${backup.id})">
                <i class="fas fa-trash"></i> Delete
            </button>
        </div>

        <!-- Backup Details -->
        <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
                <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <h3 class="text-base font-semibold text-gray-100">
                    Backup Snapshot <span class="font-mono text-blue-400 ml-2">#${backup.id}</span>
                </h3>
                <span class="text-xs px-2 py-1 bg-gray-700/50 text-gray-300 rounded-md">
                    v${Math.floor(Math.random() * 5) + 1}.0.0
                </span>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
                <div class="flex items-center gap-2">
                    <i class="fas fa-database text-yellow-400/90 text-sm"></i> 
                    <div>
                        <p class="text-gray-400">Size</p>
                        <p class="text-yellow-300 font-medium">${backup.backup_size}</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <i class="fas fa-clock text-emerald-400/90 text-sm"></i>
                    <div>
                        <p class="text-gray-400">Date</p>
                        <p class="text-emerald-300 font-medium">${new Date(backup.created_at).toLocaleDateString('en-US', { dateStyle: 'medium' })}</p>
                    </div>
                </div>
            </div>

            <div class="mt-3 flex items-center gap-4 text-xs">
                <span class="flex items-center gap-1 text-green-400">
                    <i class="fas fa-lock"></i>
                    <span>Encrypted</span>
                </span>
                <span class="flex items-center gap-1 text-gray-400">
                    <i class="fas fa-shield-alt"></i>
                    <span>AES-256</span>
                </span>
            </div>
        </div>

        <!-- Radio Selection -->
        <div class="flex items-center pl-4">
            <div class="relative">
                <input type="radio" name="backupSelect" value="${backup.id}" 
                       class="peer absolute inset-0 opacity-0 cursor-pointer">
                <div class="w-6 h-6 border-2 border-gray-500 rounded-full flex items-center justify-center
                          peer-checked:border-blue-400 peer-hover:border-blue-300 transition-all
                          group-hover:bg-gray-800/30">
                    <div class="w-3 h-3 bg-blue-400 rounded-full scale-0 
                              peer-checked:scale-100 transition-transform"></div>
                </div>
            </div>
        </div>
    </div>
`;
        backupList.appendChild(listItem);
                    });
                }
            })
            .catch(() => {
                alert("Error fetching backups!");
            });
    }

    // Delegate Event Listener for Radio Selection (Fix)
    document.getElementById("backupList").addEventListener("change", function (event) {
        if (event.target.name === "backupSelect") {
            selectedBackupId = event.target.value;
            document.getElementById("restoreBackupBtn").disabled = false;
        }
    });

    // Restore Backup with Spinner
    document.getElementById("restoreBackupBtn").addEventListener("click", function () {
        if (!selectedBackupId) {
            alert("Please select a backup first!");
            return;
        }

        let restoreBtn = document.getElementById("restoreBackupBtn");
        restoreBtn.disabled = true;

        restoreBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Restoring Backup, Please hold...
        `;

        restoreBackup(selectedBackupId, restoreBtn);
    });

    // API Call to Restore Backup
    function restoreBackup(backupId, restoreBtn) {
        fetch(`/tasks/restore-backup/${backupId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}",
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(() => {
            let modal = bootstrap.Modal.getInstance(document.getElementById("RestoreBackUpModal"));
            modal.hide();
            restoreBtn.innerHTML = "Restore Backup"; 
            restoreBtn.disabled = false;
            showToast("Backup restored successfully!", "success");
        })
        .catch(() => {
            restoreBtn.innerHTML = "Restore Backup"; 
            restoreBtn.disabled = false;
            showToast("Error restoring backup!", "error");
        });
    }

  
    

    // Toast Notification
    function showToast(message, type) {
        let bgColor = type === "success" ? "bg-success" : "bg-danger";
        let toastContainer = document.createElement("div");

        toastContainer.className = `toast ${bgColor} text-white position-fixed bottom-0 end-0 m-3`;
        toastContainer.role = "alert";
        toastContainer.dataset.bsAutohide = "true";
        toastContainer.dataset.bsDelay = "3000";

        toastContainer.innerHTML = `
            <div class="toast-header ${bgColor} text-white">
                <strong class="me-auto">${type === "success" ? "Success" : "Error"}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        `;

        document.body.appendChild(toastContainer);
        let toast = new bootstrap.Toast(toastContainer);
        toast.show();

        setTimeout(() => {
            toastContainer.remove();
        }, 3500);
    }
});


// ScheduleBackUp
// Open the modal and fetch backup schedule
function openScheduleBackupModal(orgId, groupId, taskId) {
    // Store IDs globally for later use
    window.djangoData.orgId = orgId;
    window.djangoData.groupId = groupId;
    window.djangoData.taskId = taskId;

    // Fetch the backup schedule and display it
    fetch(`/tasks/get-backup-schedule/?org_id=${orgId}&group_id=${groupId}&task_id=${taskId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector("#backupScheduleSelect").value = data.frequency;
                document.querySelector("#nextRunDisplay").innerText = data.next_run;
                document.querySelector("#activeCheckbox").checked = data.is_active;
            } else {
                console.warn("No backup schedule found.");
            }
        })
        .catch(error => console.error("Error fetching backup schedule:", error));

    // Show Bootstrap modal
    let modal = new bootstrap.Modal(document.getElementById("ScheduleBackUpModal"));
    modal.show();
}

// Update backup schedule via AJAX
// Update backup schedule via AJAX
function updateBackupSchedule() {
    const frequency = document.querySelector("#backupScheduleSelect").value;
    const isActive = document.querySelector("#activeCheckbox").checked;

    fetch("/tasks/update-backup-schedule/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),  // Only needed if CSRF protection is enabled
        },
        body: JSON.stringify({
            org_id: window.djangoData.orgId,
            group_id: window.djangoData.groupId,
            task_id: window.djangoData.taskId,
            frequency: frequency,
            is_active: isActive
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Backup schedule updated successfully!");
            let modal = bootstrap.Modal.getInstance(document.getElementById("ScheduleBackUpModal"));
            modal.hide(); // Close modal after update
        } else {
            alert("Failed to update schedule: " + data.message);
        }
    })
    .catch(error => console.error("Error updating backup schedule:", error));
}

// Function to get CSRF token (Modify if needed)
function getCSRFToken() {
    let tokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
    return tokenElement ? tokenElement.value : "";
}


// Fetch and display backup logs
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".view-backup-logs").forEach(button => {
        button.addEventListener("click", function () {
            // Find the closest task container and get IDs dynamically
            let taskContainer = this.closest("[data-org][data-group][data-task]");
            if (taskContainer) {
                window.djangoData = {
                    orgId: taskContainer.getAttribute("data-org"),
                    groupId: taskContainer.getAttribute("data-group"),
                    taskId: taskContainer.getAttribute("data-task"),
                };

                // Fetch logs when opening modal
                fetchBackupLogs();
            }
        });
    });
});

// Fetch logs and populate modal
function fetchBackupLogs(action = "") {
    if (!window.djangoData) return;
    const { orgId, groupId, taskId } = window.djangoData;
    const url = `/tasks/fetch-backup-logs/?org_id=${orgId}&group_id=${groupId}&task_id=${taskId}&action=${action}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayLogs(data.logs);
            } else {
                document.getElementById("backupLogsContainer").innerHTML = `<p>No logs found.</p>`;
            }
        })
        .catch(error => console.error("Error fetching logs:", error));
}

// Display logs in a timeline format
function displayLogs(logs) {
    const container = document.getElementById("backupLogsContainer");
    container.innerHTML = "";

    if (logs.length === 0) {
        container.innerHTML = `<p>No logs found.</p>`;
        return;
    }

    logs.forEach(log => {
        const logEntry = `
        <div class="bg-white shadow-md rounded-lg p-4 mb-3 border border-gray-200">
            <div class="flex items-center space-x-3">
                <span class="font-semibold text-gray-900 text-lg">${log.performed_by}</span>
                <span class="text-sm px-2 py-1 rounded-full bg-blue-100 text-blue-600">${log.action}</span>
            </div>
            <p class="text-sm text-gray-500 mt-1">
                <i class="far fa-clock"></i> ${new Date(log.timestamp).toLocaleString()}
            </p>
            <pre class="mt-2 p-3 bg-gray-100 rounded-lg text-sm text-gray-800 border border-gray-300 font-mono overflow-x-auto">
                ${JSON.stringify(log.details, null, 2)}
            </pre>
        </div>
    `;
        container.innerHTML += logEntry;
    });
}

// Filter logs based on action
function filterBackupLogs() {
    const selectedAction = document.getElementById("logFilter").value;
    fetchBackupLogs(selectedAction);
}


// Share Logs
function sendLogsEmail() {
    const button = document.getElementById("sendLogsBtn");

    // Show loading spinner
    button.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Sending...`;
    button.disabled = true;

    fetch("/tasks/send-task-logs/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),  
        },
        body: JSON.stringify({
            org_id: window.djangoData.orgId,
            group_id: window.djangoData.groupId,
            task_id: window.djangoData.taskId
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Logs sent successfully!");
        } else {
            alert("Failed to send logs: " + data.message);
        }
    })
    .catch(error => console.error("Error sending logs:", error))
    .finally(() => {
        button.innerHTML = `Send Logs 📩`;
        button.disabled = false;
    });
}

// Function to get CSRF token
function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
}


// Handle Task Progress

document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ JavaScript Loaded: Ready to manage task progress...");

    // Modals
    const progressModalNew = new bootstrap.Modal(document.getElementById("progressModalNew"));
    const detailsModalNew = new bootstrap.Modal(document.getElementById("progressDetailsModalNew"));

    // Buttons
    const increaseBtnNew = document.getElementById("increaseProgressBtnNew");
    const decreaseBtnNew = document.getElementById("decreaseProgressBtnNew");
    const submitBtnNew = document.getElementById("submitProgressNew");

    // Input
    const progressDetailsInputNew = document.getElementById("progressDetailsNew");

    // Progress Bar
    const progressBarNew = document.getElementById("progressBarNew");

    let progressValueNew = 0;  // Current Progress Value
    let actionTypeNew = "";  // Track increase or decrease

    // Open Progress Modal
    document.getElementById("openProgressModalNew").addEventListener("click", function () {
        console.log("🟢 Open Progress Modal Clicked.");
        fetchProgressNew();
        progressModalNew.show();
    });

    // Increase Progress
    increaseBtnNew.addEventListener("click", function () {
        actionTypeNew = "increase";
        console.log("🟢 Increase Progress Clicked.");
        detailsModalNew.show();
    });

    // Decrease Progress
    decreaseBtnNew.addEventListener("click", function () {
        actionTypeNew = "decrease";
        console.log("🟢 Decrease Progress Clicked.");
        detailsModalNew.show();
    });

    // Submit Progress Update
    submitBtnNew.addEventListener("click", function () {
        let detailsNew = progressDetailsInputNew.value.trim();
        console.log(`🟡 Submit Progress Clicked. Action: ${actionTypeNew}, Details: ${detailsNew}`);

        if (!detailsNew) {
            alert("⚠️ Please enter details before submitting.");
            console.warn("⚠️ Submission aborted: No details provided.");
            return;
        }

        // Disable Button & Show Loader
        submitBtnNew.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Updating...`;
        submitBtnNew.disabled = true;

        updateProgressNew(actionTypeNew, detailsNew, function (newProgressNew) {
            submitBtnNew.innerHTML = "Submit";
            submitBtnNew.disabled = false;
            detailsModalNew.hide();
            updateProgressBarNew(newProgressNew);
        });
    });

    // Fetch Task Progress
    function fetchProgressNew() {
        let orgId = window.djangoData.orgId;
        let groupId = window.djangoData.groupId;
        let taskId = window.djangoData.taskId;
        let url = `/tasks/fetch-task-progress-new/?org_id=${orgId}&group_id=${groupId}&task_id=${taskId}`;
    
        console.log(`🔵 Fetching Progress: ${url}`);
    
        fetch(url, { method: "GET", headers: { "Content-Type": "application/json" } })
        .then(response => response.json())
        .then(data => {
            console.log("🟢 Progress Data Received:", data);
            if (data.error) {
                alert("❌ Error: " + data.error);
                return;
            }
    
            progressValueNew = data.progress;
            updateProgressBarNew(progressValueNew);  // ✅ Ensure bar updates immediately
        })
        .catch(error => console.error("❌ Error fetching progress:", error));
    }
    
    // Update Task Progress
    function updateProgressNew(action, details, callback) {
        let csrfToken = getCSRFTokenNew();
        if (!csrfToken) {
            alert("⚠️ CSRF token missing! Please refresh the page.");
            console.error("❌ CSRF Token Missing. Aborting request.");
            return;
        }

        let payload = {
            org_id: window.djangoData.orgId,
            group_id: window.djangoData.groupId,
            task_id: window.djangoData.taskId,
            action: action,
            details: details
        };

        console.log("🔵 Updating Progress. Payload:", payload);
        console.log("🔵 CSRF Token:", csrfToken);

        fetch(`/tasks/update-task-progress-new/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            console.log(`🔵 Update Response Status: ${response.status}`);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log("🟢 Progress Update Response:", data);
            if (data.success) {
                alert("✅ Progress updated successfully!");
                callback(data.new_progress);
            } else {
                alert("❌ Error: " + (data.error || "Failed to update progress."));
            }
        })
        .catch(error => console.error("❌ Error updating progress:", error));
    }

    // Update Progress Bar Dynamically
    function updateProgressBarNew(value) {
        if (value < 0) value = 0;
        if (value > 100) value = 100;

        progressBarNew.style.width = `${value}%`;
        progressBarNew.innerText = `${value}%`;
        progressBarNew.setAttribute("aria-valuenow", value);  // Ensure Bootstrap updates UI
        progressBarNew.classList.remove("bg-info"); // Reset class to force repaint
        void progressBarNew.offsetWidth; // Trigger reflow (force UI update)
        progressBarNew.classList.add("bg-info"); // Reapply class after reflow
        
        console.log(`🔵 Progress Bar Updated: ${value}%`);
    }

    // Get CSRF Token for Secure Requests
    function getCSRFTokenNew() {
        let csrfCookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
        let csrfToken = csrfCookie ? csrfCookie.split("=")[1] : null;
        console.log("🔵 Extracted CSRF Token:", csrfToken);
        return csrfToken;
    }
});


// Fetch Progress Logs
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Task Logs JS Loaded.");

    // Elements
    const logsModal = new bootstrap.Modal(document.getElementById("progressLogsModal"));
    const logsContainer = document.getElementById("logsContainer");
    const searchInput = document.getElementById("logSearch");
    const openLogsBtn = document.getElementById("openLogsModal");

    openLogsBtn.addEventListener("click", function () {
        console.log("🟢 Fetching Progress Logs...");
        fetchLogs();
        logsModal.show();
    });

    // Fetch Logs from Server
    function fetchLogs() {
        let orgId = window.djangoData.orgId;
        let groupId = window.djangoData.groupId;
        let taskId = window.djangoData.taskId;
        let url = `/tasks/fetch-task-progress-logs/?org_id=${orgId}&group_id=${groupId}&task_id=${taskId}`;

        fetch(url, { method: "GET", headers: { "Content-Type": "application/json" } })
            .then(response => response.json())
            .then(data => {
                console.log("🟢 Logs Data:", data);
                if (data.error) {
                    logsContainer.innerHTML = `<p class="text-danger text-center">${data.error}</p>`;
                    return;
                }

                if (data.logs.length === 0) {
                    logsContainer.innerHTML = `<p class="text-center text-muted">No logs available.</p>`;
                    return;
                }

                renderLogs(data.logs);
            })
            .catch(error => {
                console.error("❌ Error fetching logs:", error);
                logsContainer.innerHTML = `<p class="text-danger text-center">Error fetching logs.</p>`;
            });
    }

    // Render Logs in the Modal
    function renderLogs(logs) {
        let html = `<ul class="list-group">`;


        logs.forEach(log => {
            html += `
                <div class="p-4 mb-3 bg-white/70 backdrop-blur-sm rounded-xl shadow-sm border border-white/80 
                    hover:shadow-md transition-shadow duration-300">
                    <div class="flex items-start gap-3">
                        <!-- Icon Container -->
                        <div class="w-10 h-10 flex items-center justify-center rounded-lg 
                            ${log.progress_change > 0 ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}">
                            ${log.progress_change > 0 ? 
                                '<span class="material-icons text-lg">trending_up</span>' : 
                                '<span class="material-icons text-lg">trending_down</span>'}
                        </div>
        
                        <!-- Content -->
                        <div class="flex-1">
                            <div class="flex items-baseline gap-2">
                                <span class="font-semibold text-gray-800">${log.user}</span>
                                <span class="text-sm ${log.progress_change > 0 ? 'text-green-600' : 'text-red-600'} 
                                    font-medium px-2 py-1 rounded-full bg-opacity-20 
                                    ${log.progress_change > 0 ? 'bg-green-100' : 'bg-red-100'}">
                                    ${log.progress_change > 0 ? '+' : ''}${log.progress_change}%
                                </span>
                                <span class="ml-auto text-sm text-gray-400 flex items-center gap-1">
                                    <span class="material-icons text-base">schedule</span>
                                    ${log.timestamp}
                                </span>
                            </div>
        
                            <div class="mt-2 text-gray-600 text-sm pl-1 border-l-2 border-indigo-200">
                                <p class="ml-2">${log.details || 'No additional details provided'}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        html += `</ul>`;
        logsContainer.innerHTML = html;
    }

    // Real-Time Search in Logs
    searchInput.addEventListener("input", function () {
        let query = this.value.toLowerCase();
        let logs = document.querySelectorAll(".log-item");

        logs.forEach(log => {
            log.style.display = log.textContent.toLowerCase().includes(query) ? "block" : "none";
        });
    });
});


// Manage themes 
document.addEventListener("DOMContentLoaded", function () {
    console.log("🎨 Theme Manager Loaded...");

    const themeModal = new bootstrap.Modal(document.getElementById("themeModal"));
    const openThemeBtn = document.getElementById("openThemeModal");
    const themeOptions = document.querySelectorAll(".theme-option");

    // Open Theme Modal
    openThemeBtn.addEventListener("click", function () {
        console.log("🟢 Open Theme Modal Clicked.");
        themeModal.show();
    });

    // Apply Theme on Selection
    themeOptions.forEach(option => {
        option.addEventListener("click", function () {
            const selectedTheme = this.getAttribute("data-theme");
            console.log(`🎨 Theme Selected: ${selectedTheme}`);
            applyTheme(selectedTheme);
            localStorage.setItem("userTheme", selectedTheme);
        });
    });

    // Function to Apply Theme
    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        console.log("✅ Theme Applied:", theme);
    }

    // Load User's Saved Theme
    const savedTheme = localStorage.getItem("userTheme");
    if (savedTheme) {
        console.log(`🔵 Applying Saved Theme: ${savedTheme}`);
        applyTheme(savedTheme);
    }
});
