

// SHARE THE TASK WITH TEAM-MEMBERS
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
