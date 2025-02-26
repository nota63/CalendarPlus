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
// MANAGE TASKIFY BOARD
document.addEventListener("DOMContentLoaded", function () {
    const openModal = document.getElementById("openMangeTaskifyModal");
    const closeModal = document.getElementById("closeMangeTaskifyModal");
    const modal = document.getElementById("MangeTaskifyModal");

    const columns = {
        pending: document.getElementById("pendingTasks"),
        in_progress: document.getElementById("inProgressTasks"),
        completed: document.getElementById("completedTasks"),
        blocked: document.getElementById("blockedTasks"),
    };

    const orgId = window.djangoData.orgId;

    if (openModal) {
        openModal.addEventListener("click", function () {
            modal.classList.remove("hidden");
            fetchTasks();
        });
    }

    if (closeModal) {
        closeModal.addEventListener("click", function () {
            modal.classList.add("hidden");
        });
    }

    function getCSRFToken() {
        let cookieValue = null;
        document.cookie.split(";").forEach(cookie => {
            let [name, value] = cookie.trim().split("=");
            if (name === "csrftoken") {
                cookieValue = decodeURIComponent(value);
            }
        });
        return cookieValue;
    }

    function fetchTasks() {
        fetch(`/taskify/get-tasks/${orgId}/`)
            .then(response => response.json())
            .then(data => {
                Object.keys(columns).forEach(status => {
                    columns[status].innerHTML = "";
                    data[status].forEach(task => {
                        let taskElement = document.createElement("div");
                        taskElement.classList.add("task-item", "bg-white", "p-2", "rounded-lg", "shadow", "cursor-pointer");
                        taskElement.setAttribute("draggable", "true");
                        taskElement.setAttribute("data-task-id", task.id);
                        taskElement.textContent = task.title;
                        taskElement.addEventListener("dragstart", dragStart);
                        columns[status].appendChild(taskElement);
                    });
                });
            })
            .catch(error => console.error("Error fetching tasks:", error));
    }

    function dragStart(event) {
        event.dataTransfer.setData("taskId", event.target.dataset.taskId);
    }

    Object.keys(columns).forEach(status => {
        columns[status].addEventListener("dragover", function (event) {
            event.preventDefault();
        });

        columns[status].addEventListener("drop", function (event) {
            event.preventDefault();
            let taskId = event.dataTransfer.getData("taskId");
            let newStatus = status;
            updateTaskStatus(taskId, newStatus);
        });
    });

    function updateTaskStatus(taskId, newStatus) {
        fetch("/taskify/update-task-status/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ task_id: taskId, new_status: newStatus }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    fetchTasks();
                } else {
                    alert("Failed to update task status!");
                }
            })
            .catch(error => console.error("Error updating task:", error));
    }
});
