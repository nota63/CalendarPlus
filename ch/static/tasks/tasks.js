
// DELETE THE TASK - MANAGER ONLY
document.addEventListener("DOMContentLoaded", function () {
    const confirmDeleteBtn = document.getElementById("confirmDeleteTask");
    const errorMsg = document.getElementById("taskDeleteError");
    const successPopup = document.getElementById("taskDeleteSuccessPopup");

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
                "X-CSRFToken": getCSRFToken()
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
                // ✅ Show Success Pop-up
                successPopup.style.opacity = "1";
                successPopup.style.visibility = "visible";

                // ✅ Redirect after 2 seconds
                setTimeout(() => {
                    const redirectURL = `http://127.0.0.1:8000/tasks/tasks/assigned-users/${window.djangoData.orgId}/${window.djangoData.groupId}/`;
                    window.location.href = redirectURL;
                }, 2000);
            } else {
                errorMsg.textContent = data.message;
            }
        })
        .catch(error => {
            errorMsg.textContent = "Something went wrong. Try again.";
        });
    });
});
