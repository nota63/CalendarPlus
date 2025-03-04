// CHECK FOR COMMANDS 
document.addEventListener("DOMContentLoaded", function () {
    const cmdInput = document.getElementById("cmdInput");

    // Get all commands dynamically from app.mini_app.commands
    let appCommands = new Set();
    document.querySelectorAll(".bg-white\\/5 span.ml-2").forEach(span => {
        appCommands.add(span.textContent.trim());
    });

    // Function to check if user-entered command exists in appCommands
    function checkCommand(command) {
        if (!appCommands.has(command)) {
            alert(`Error: '${command}' is not available in this app.`);
            setTimeout(() => {
                location.reload(); // Reload the page to stop all operations
            }, 0000); // Delay for smooth UX
            return false;
        }
        return true;
    }

    // Automatically listen for user input and validate commands
    cmdInput.addEventListener("keyup", function (event) {
        if (event.key === "Enter") {
            let command = cmdInput.value.trim();

            if (!checkCommand(command)) {
                return; // Stop everything if command is invalid
            }

            // If command is valid, trigger a custom event
            document.dispatchEvent(new CustomEvent("commandEntered", { detail: { command } }));
        }
    });
});







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
        // Check if `/channels` exists in available commands
        if (!availableCommands.includes("/channels")) {
            alert("Error: /channels command is not available in this app.");
            return;
        }

        // Fetch Organization ID & App ID (Modify as needed)
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
                    ${channel.name}
                    <button class="btn btn-primary btn-sm open-channel" data-id="${channel.id}">Open Channel</button>
                `;

                channelsList.appendChild(listItem);
            });

            // Add event listeners to buttons
            document.querySelectorAll(".open-channel").forEach(button => {
                button.addEventListener("click", function () {
                    let channelId = this.getAttribute("data-id");
                    window.location.href = `http://127.0.0.1:8000/channels/channel/${channelId}/chat/`;
                });
            });
        }

        // Show the Bootstrap modal
        let channelsModal = new bootstrap.Modal(document.getElementById("channelsModal"));
        channelsModal.show();
    }
});
