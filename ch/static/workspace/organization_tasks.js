// CREATE THE TASK
document.addEventListener("DOMContentLoaded", function () {
    const openModal = document.getElementById("openTaskModal");
    const closeModal = document.getElementById("closeTaskModal");
    const modal = document.getElementById("TaskModal");
    const taskForm = document.getElementById("taskForm");

    if (openModal && closeModal && modal && taskForm) {
        openModal.addEventListener("click", () => {
            modal.classList.remove("hidden");
        });

        closeModal.addEventListener("click", () => {
            modal.classList.add("hidden");
        });

        taskForm.addEventListener("submit", function (event) {
            event.preventDefault();

            let orgIdElement = document.getElementById("orgId");
            if (!orgIdElement) {
                alert("Organization ID not found!");
                return;
            }

            let orgId = window.djangoData.orgId;
            let title = document.getElementById("taskTitle").value.trim();
            let description = document.getElementById("taskDescription").value.trim();
            let priority = document.getElementById("taskPriority").value;
            let dueDate = document.getElementById("taskDueDate").value;

            if (!title) {
                alert("Task title is required!");
                return;
            }

            // ✅ Get CSRF Token from Cookie
            function getCSRFToken() {
                let cookieValue = null;
                if (document.cookie && document.cookie !== "") {
                    document.cookie.split(";").forEach(cookie => {
                        let [name, value] = cookie.trim().split("=");
                        if (name === "csrftoken") {
                            cookieValue = decodeURIComponent(value);
                        }
                    });
                }
                return cookieValue;
            }

            let taskData = {
                org_id: orgId,
                title: title,
                description: description,
                priority: priority,
                due_date: dueDate,
            };

            fetch("/taskify/create-task/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()  // ✅ Sending CSRF token
                },
                body: JSON.stringify(taskData),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert("Task Created Successfully!");
                    modal.classList.add("hidden");
                    taskForm.reset();
                } else {
                    alert("Failed to create task!");
                }
            })
            .catch(error => console.error("Error:", error));
        });
    } else {
        console.error("Modal elements not found in the DOM!");
    }
});



// MANAGE TASKS BOARD
// MANAGE TASKS BOARD
document.getElementById("open-kanban").addEventListener("click", function () {
    document.getElementById("kanban-modal").style.display = "block";
    fetchTasks();
});

document.querySelector(".close").addEventListener("click", function () {
    document.getElementById("kanban-modal").style.display = "none";
});

function fetchTasks() {
    let orgId = window.djangoData?.orgId; // Get org ID from template safely
    if (!orgId) {
        console.error("Organization ID is missing.");
        return;
    }

    fetch(`/taskify/get-tasks/${orgId}/`)
        .then(response => response.json())
        .then(data => {
            let statuses = { "pending": [], "in_progress": [], "completed": [], "blocked": [] };
            data.tasks.forEach(task => {
                let taskElement = `
                    <div class="kanban-item" data-id="${task.id}" style="
                        background: white;
                        padding: 12px;
                        margin: 8px 0;
                        border-radius: 8px;
                        box-shadow: 2px 4px 6px rgba(0, 0, 0, 0.1);
                        font-weight: 500;
                        cursor: grab;
                        transition: transform 0.2s;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        ${task.title}
                    </div>`;
                statuses[task.status].push(taskElement);
            });

            Object.keys(statuses).forEach(status => {
                let column = document.getElementById(status);
                if (column) column.innerHTML = statuses[status].join("");
            });

            setupDragDrop();
        })
        .catch(error => console.error("Error fetching tasks:", error));
}

function setupDragDrop() {
    ["pending", "in_progress", "completed", "blocked"].forEach(id => {
        let column = document.getElementById(id);
        if (column) {
            column.style.cssText = `
                background: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 12px;
                min-height: 250px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                overflow-y: auto;
                max-height: 400px;
            `;

            new Sortable(column, {
                group: "kanban",
                animation: 150,
                onEnd: function (evt) {
                    let taskId = evt.item.getAttribute("data-id");
                    let newStatus = evt.to.getAttribute("id");
                    updateTaskStatus(taskId, newStatus);
                }
            });
        }
    });
}

function updateTaskStatus(taskId, newStatus) {
    let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrfToken) {
        console.error("CSRF token is missing.");
        return;
    }

    fetch(`/taskify/update_task_status/${taskId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({ status: newStatus })
    })
        .then(response => response.json())
        .then(data => console.log("Task updated!", data))
        .catch(error => console.error("Error updating task:", error));
}
