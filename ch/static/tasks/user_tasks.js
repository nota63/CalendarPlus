

// SHARE THE TASK WITH TEAM-MEMBERS
document.addEventListener("DOMContentLoaded", function () {
    const openModalBtn = document.getElementById("openShareTaskModal");
    const sendTaskBtn = document.getElementById("sendTaskBtn");
    const sendSpinner = document.getElementById("sendSpinner");
    const membersList = document.getElementById("membersList");
    
    let orgId, groupId, taskId, selectedMembers = [];

    // ✅ Open Modal & Fetch Members
    openModalBtn.addEventListener("click", function () {
        orgId =window.djangoData.orgId;
        groupId =window.djangoData.groupId;
        taskId =window.djangoData.taskId;

        fetch(`/tasks/get-workspace-members/?org_id=${orgId}`)
        .then(response => response.json())
        .then(data => {
            membersList.innerHTML = ""; // Clear existing members
            if (data.status === "success") {
                data.members.forEach(member => {
                    const memberCard = document.createElement("div");
                    memberCard.className = "d-flex align-items-center p-2 border rounded";
                    memberCard.innerHTML = `
                        <img src="${member.profile_picture}" class="rounded-circle" width="40" height="40">
                        <span class="ms-2">${member.full_name}</span>
                        <input type="checkbox" value="${member.user_id}" class="ms-auto form-check-input">
                    `;
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
        selectedMembers = [...membersList.querySelectorAll("input:checked")].map(input => input.value);

        if (selectedMembers.length === 0) {
            alert("Please select at least one member!");
            return;
        }

        sendTaskBtn.disabled = true;
        sendSpinner.classList.remove("d-none");

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
            sendSpinner.classList.add("d-none");
        });
    });
});
