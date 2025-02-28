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


// -------------------------------------------------------------------------------------------------------------------

// Edit Profile
// Edit Profile
document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("editProfileModal");
    const fullNameInput = document.getElementById("full_name");
    const profilePictureInput = document.getElementById("profile_picture");
    const profilePreview = document.getElementById("profile_preview");
    const updateProfileForm = document.getElementById("updateProfileForm");
    const meetingCount = document.getElementById("meeting_count"); // Meeting count element
    const eventCount = document.getElementById("event_count"); // Event count element
    const bookingCount = document.getElementById("booking_count"); // Booking count element
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value; // Get CSRF token

    if (!csrfToken) {
        console.error("CSRF token not found!");
    }

    let orgId = window.djangoData?.orgId; // Ensure org_id is dynamically set

    if (!orgId) {
        console.error("Organization ID is missing!");
    }

    // Fetch profile details when modal opens
    modal.addEventListener("show.bs.modal", function() {
        console.log("Fetching profile data for orgId:", orgId);
        fetch(`/taskify/ajax-profile-edit/${orgId}/`, {
            method: "GET",
            headers: { "X-CSRFToken": csrfToken }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Profile fetch response:", data);
            if (data.success) {
                let profile = data.profile;
                fullNameInput.value = profile.full_name;

                if (profile.profile_picture) {
                    profilePreview.src = profile.profile_picture;
                    profilePreview.style.display = "block";
                } else {
                    profilePreview.style.display = "none";
                }

                // ✅ Update counts dynamically
                meetingCount.textContent = profile.meetings || 0;
                eventCount.textContent = profile.events || 0;
                bookingCount.textContent = profile.bookings || 0;

            } else {
                console.error("Failed to fetch profile data:", data.error);
                alert("Failed to fetch profile data.");
            }
        })
        .catch(error => console.error("Error fetching profile:", error));
    });

    // Handle profile update with image upload
    updateProfileForm.addEventListener("submit", function(e) {
        e.preventDefault();
        console.log("Submitting profile update for orgId:", orgId);

        let formData = new FormData(updateProfileForm);
        formData.append("csrfmiddlewaretoken", csrfToken); // Append CSRF token

        fetch(`/taskify/ajax-profile-edit/${orgId}/`, {
            method: "POST",
            body: formData,
            headers: { "X-CSRFToken": csrfToken }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Profile update response:", data);
            if (data.success) {
                alert("Profile updated successfully!");
                if (data.profile_picture) {
                    document.getElementById("profile_img_navbar").src = data.profile_picture; // Update navbar image
                }
                let bsModal = bootstrap.Modal.getInstance(modal);
                bsModal.hide(); // Close modal
            } else {
                console.error("Error updating profile:", data.error);
                alert("Error: " + data.error);
            }
        })
        .catch(error => console.error("Error updating profile:", error));
    });

    // Preview new profile picture before upload
    profilePictureInput.addEventListener("change", function() {
        let reader = new FileReader();
        reader.onload = function(e) {
            profilePreview.src = e.target.result;
            profilePreview.style.display = "block";
        };
        reader.readAsDataURL(profilePictureInput.files[0]);
    });
});
