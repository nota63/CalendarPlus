


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
// Open Automation Modal
document.getElementById("openAutomationModal").addEventListener("click", function () {
    const orgId = window.djangoData.orgId;
    const groupId = window.djangoData.groupId;
    const taskId = window.djangoData.taskId;

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
        const proceededList = document.getElementById("proceededList");
        const runningList = document.getElementById("runningList");

        proceededList.innerHTML = "";
        runningList.innerHTML = "";

        let hasProceeded = false;
        let hasRunning = false;

        // Populate Proceeded List
        if (data.proceeded && Object.keys(data.proceeded).length > 0) {
            hasProceeded = true;
            Object.keys(data.proceeded).forEach(key => {
                const listItem = document.createElement("li");
                listItem.className = "p-2 bg-green-100 text-green-800 rounded";
                listItem.innerHTML = `<strong>${formatKey(key)}:</strong> ✅ Proceeded`;
                proceededList.appendChild(listItem);
            });
        } else {
            proceededList.innerHTML = `<li class="p-2 text-gray-500">No automations proceeded yet.</li>`;
        }

        // Populate Running List
        if (data.running && Object.keys(data.running).length > 0) {
            hasRunning = true;
            Object.keys(data.running).forEach(key => {
                const listItem = document.createElement("li");
                listItem.className = "p-2 bg-yellow-100 text-yellow-800 rounded";
                listItem.innerHTML = `<strong>${formatKey(key)}:</strong> ⏳ Running`;
                runningList.appendChild(listItem);
            });
        } else {
            runningList.innerHTML = `<li class="p-2 text-gray-500">No running automations.</li>`;
        }

        // Show/Hide Sections Based on Data
        proceededList.style.display = hasProceeded ? "block" : "none";
        runningList.style.display = hasRunning ? "block" : "none";

        // Show Modal
        document.getElementById("AutomationStatusModal").classList.remove("hidden");
    })
    .catch(error => {
        console.error("Error fetching automation status:", error);
        document.getElementById("proceededList").innerHTML = `<li class="p-2 text-red-500">Error loading data.</li>`;
        document.getElementById("runningList").innerHTML = `<li class="p-2 text-red-500">Error loading data.</li>`;
    });
});

// Close Modal
document.getElementById("closeAutomationModal").addEventListener("click", function () {
    document.getElementById("AutomationStatusModal").classList.add("hidden");
});

document.getElementById("closeAutomationModalFooter").addEventListener("click", function () {
    document.getElementById("AutomationStatusModal").classList.add("hidden");
});

// Toggle Sections
document.getElementById("toggleProceeded").addEventListener("click", function () {
    document.getElementById("proceededList").classList.toggle("hidden");
});

document.getElementById("toggleRunning").addEventListener("click", function () {
    document.getElementById("runningList").classList.toggle("hidden");
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
