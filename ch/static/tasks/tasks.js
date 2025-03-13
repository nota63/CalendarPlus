
// DELETE THE TASK - MANAGER ONLY
document.addEventListener("DOMContentLoaded", function () {
    const confirmDeleteBtn = document.getElementById("confirmDeleteTask");
    const errorMsg = document.getElementById("taskDeleteError");

    // ✅ Generate CSRF token dynamically from Django cookie
    function getCSRFToken() {
        let cookieValue = null;
        const cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) {
                cookieValue = cookie.substring("csrftoken=".length);
                break;
            }
        }
        return cookieValue;
    }

    confirmDeleteBtn.addEventListener("click", function () {
        const password = document.getElementById("taskDeletePassword").value;

        if (!password.trim()) {
            errorMsg.textContent = "Password is required!";
            return;
        }

        fetch("/tasks/task-delete-view/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()  // ✅ Now generates CSRF dynamically
            },
            body: JSON.stringify({
                task_id: window.djangoData.taskId,
                org_id: window.djangoData.orgId,
                group_id: window.djangoData.groupId,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("Task deleted successfully!");
                location.reload();
            } else {
                errorMsg.textContent = data.message;
            }
        })
        .catch(error => {
            errorMsg.textContent = "Something went wrong. Try again.";
        });
    });
});
