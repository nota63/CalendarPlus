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
        console.log(`📡 Fetching URL: /apps/add_task_workspace/${orgId}/${appId}/`);
        console.log("🛡️ CSRF Token:", csrfToken);

        fetch(`/apps/add_task_workspace/${orgId}/${appId}/`, {
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
                console.log("Fetched Tasks:", data); // ✅ DEBUG API RESPONSE
                if (data.tasks && Array.isArray(data.tasks)) {
                    renderKanbanBoard(data.tasks);
                } else {
                    console.error("Invalid tasks data:", data);
                }
            })
            .catch(error => console.error("Error fetching Kanban tasks:", error));
    }

    function renderKanbanBoard(tasks) {
        console.log("Rendering tasks:", tasks); // ✅ DEBUG TASKS

        const kanban = new jKanban({
            element: "#kanban-board",
            gutter: "10px",
            widthBoard: "250px",
            boards: [
                { id: "todo", title: "📝 To Do", item: [] },
                { id: "in_progress", title: "🚀 In Progress", item: [] },
                { id: "done", title: "✅ Done", item: [] }
            ],
            dragendEl: function (el, source) {
                updateTaskStatus(el.dataset.eid, source.parentElement.dataset.id);
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

            console.log(`Adding task: ${task.title} in ${task.status}`); // ✅ DEBUG TASK ADDITION
            kanban.addElement(task.status, {
                id: task.id,
                title: `<strong>${task.title}</strong>`,
            });
        });
    }

    function updateTaskStatus(taskId, newStatus) {
        console.log(`Updating task ${taskId} to ${newStatus}`); // ✅ DEBUG TASK UPDATE
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
                console.log(`Task ${taskId} updated successfully!`); // ✅ DEBUG SUCCESS
            }
        })
        .catch(error => console.error("Error updating task:", error));
    }
});
