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
