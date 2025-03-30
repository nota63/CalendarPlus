
// DELETE THE TASK - MANAGER ONLY
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

        // Store original button text & add spinner
        const originalText = confirmDeleteBtn.innerHTML;
        confirmDeleteBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...`;
        confirmDeleteBtn.disabled = true; // Disable button to prevent multiple clicks

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
                confirmDeleteBtn.innerHTML = originalText; // Restore button text
                confirmDeleteBtn.disabled = false;
            }
        })
        .catch(error => {
            errorMsg.textContent = "Something went wrong. Try again.";
            confirmDeleteBtn.innerHTML = originalText; // Restore button text
            confirmDeleteBtn.disabled = false;
        });
    });
});


// Handle live in-page search
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchEverything");
    const searchControls = document.getElementById("searchControls");
    const searchCounter = document.getElementById("searchCounter");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const clearBtn = document.getElementById("clearBtn");

    let matches = [];
    let currentMatchIndex = -1;

    searchInput.addEventListener("input", function () {
        removeHighlights();
        const searchText = searchInput.value.trim().toLowerCase();

        if (searchText !== "") {
            searchControls.style.display = "block"; // Show controls
            matches = highlightMatches(searchText);
            updateCounter();
        } else {
            searchControls.style.display = "none"; // Hide controls
            matches = [];
            updateCounter();
        }
    });

    function highlightMatches(searchText) {
        const textNodes = getTextNodes(document.body);
        let foundMatches = [];

        textNodes.forEach(node => {
            const text = node.nodeValue.toLowerCase();
            if (text.includes(searchText)) {
                const regex = new RegExp(`(${searchText})`, "gi");
                const newHTML = node.nodeValue.replace(regex, `<span class="highlight">$1</span>`);

                const tempDiv = document.createElement("div");
                tempDiv.innerHTML = newHTML;

                while (tempDiv.firstChild) {
                    node.parentNode.insertBefore(tempDiv.firstChild, node);
                }

                foundMatches.push(...node.parentNode.querySelectorAll(".highlight"));
                node.parentNode.removeChild(node);
            }
        });

        return foundMatches;
    }

    function getTextNodes(element) {
        let textNodes = [];
        const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, null, false);
        while (walker.nextNode()) {
            textNodes.push(walker.currentNode);
        }
        return textNodes;
    }

    function removeHighlights() {
        document.querySelectorAll(".highlight").forEach(span => {
            span.replaceWith(span.textContent);
        });
        matches = [];
        currentMatchIndex = -1;
        updateCounter();
    }

    function updateCounter() {
        if (matches.length === 0) {
            searchCounter.textContent = "0 results";
            prevBtn.disabled = true;
            nextBtn.disabled = true;
        } else {
            searchCounter.textContent = `Result 1 of ${matches.length}`;
            currentMatchIndex = 0;
            scrollToMatch();
            prevBtn.disabled = matches.length <= 1;
            nextBtn.disabled = matches.length <= 1;
        }
    }

    function scrollToMatch() {
        if (matches.length > 0 && currentMatchIndex !== -1) {
            matches.forEach(match => match.style.backgroundColor = "yellow"); // Reset all
            matches[currentMatchIndex].style.backgroundColor = "orange"; // Highlight active
            matches[currentMatchIndex].scrollIntoView({ behavior: "smooth", block: "center" });
            searchCounter.textContent = `Result ${currentMatchIndex + 1} of ${matches.length}`;
        }
    }

    nextBtn.addEventListener("click", function () {
        if (matches.length > 0) {
            currentMatchIndex = (currentMatchIndex + 1) % matches.length;
            scrollToMatch();
        }
    });

    prevBtn.addEventListener("click", function () {
        if (matches.length > 0) {
            currentMatchIndex = (currentMatchIndex - 1 + matches.length) % matches.length;
            scrollToMatch();
        }
    });

    searchInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            nextBtn.click();
        } else if (e.key === "Enter" && e.shiftKey) {
            e.preventDefault();
            prevBtn.click();
        }
    });

    clearBtn.addEventListener("click", function () {
        searchInput.value = "";
        removeHighlights();
        searchControls.style.display = "none"; // Hide controls after clearing
    });
});


// ACCEPT THE TASK APPROVAL
document.addEventListener("DOMContentLoaded", function () {
    const openModalBtn = document.getElementById("openTaskApprovalModal");
    const approveTaskBtn = document.getElementById("approveTask");
    const rejectTaskBtn = document.getElementById("rejectTask");
    const errorMsg = document.getElementById("approvalError");
    const approveSpinner = document.getElementById("approveSpinner");
    const rejectSpinner = document.getElementById("rejectSpinner");

    let orgId, groupId, taskId;

    // ✅ Open Modal and Set Task Data
    if (openModalBtn) {
        openModalBtn.addEventListener("click", function () {
            orgId = this.getAttribute("data-org-id");
            groupId = this.getAttribute("data-group-id");
            taskId = this.getAttribute("data-task-id");

            const approvalModal = new bootstrap.Modal(document.getElementById("taskApprovalModal"));
            approvalModal.show();
        });
    }

    function handleTaskAction(action) {
        const password = document.getElementById("managerPassword").value;
        if (!password.trim()) {
            errorMsg.textContent = "Password is required!";
            return;
        }

        // ✅ Show Spinner
        if (action === "approve") {
            approveTaskBtn.disabled = true;
            approveSpinner.classList.remove("d-none");
        } else {
            rejectTaskBtn.disabled = true;
            rejectSpinner.classList.remove("d-none");
        }

        fetch("/tasks/approve-or-reject-task/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').getAttribute("content")
            },
            body: JSON.stringify({
                org_id: orgId,
                group_id: groupId,
                task_id: taskId,
                password: password,
                action: action
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                // ✅ Hide Modal
                document.getElementById("taskApprovalModal").classList.remove("show");
                document.body.classList.remove("modal-open");
                document.querySelector(".modal-backdrop").remove();

                if (data.approved) {
                    // ✅ Trigger Firecrackers Animation
                    startFireworks();
                    showSuccessMessage();
                } else {
                    alert("Task has been rejected and set to 'Need Changes'!");
                }
            } else {
                errorMsg.textContent = data.message;
            }
        })
        .finally(() => {
            // ✅ Reset Buttons & Spinners
            approveTaskBtn.disabled = false;
            rejectTaskBtn.disabled = false;
            approveSpinner.classList.add("d-none");
            rejectSpinner.classList.add("d-none");
        });
    }

    if (approveTaskBtn) {
        approveTaskBtn.addEventListener("click", () => handleTaskAction("approve"));
    }

    if (rejectTaskBtn) {
        rejectTaskBtn.addEventListener("click", () => handleTaskAction("reject"));
    }
});

// ✅ Firecracker Animation with Smooth Effect
function startFireworks() {
    const fireworksContainer = document.createElement("div");
    fireworksContainer.className = "fixed inset-0 pointer-events-none z-[9999]";
    document.body.appendChild(fireworksContainer);

    for (let i = 0; i < 500; i++) {
        const firework = document.createElement("div");
        firework.className = `
            absolute w-[3px] h-[3px] rounded-full 
            bg-gradient-to-r from-yellow-400 to-red-500 
            shadow-[0_0_8px_#f59e0b] animate-sparkle
            transition-opacity duration-1000
        `;
        firework.style.left = Math.random() * 100 + "vw";
        firework.style.top = Math.random() * 100 + "vh";
        fireworksContainer.appendChild(firework);

        // Add secondary animation effect
        setTimeout(() => {
            firework.classList.add("opacity-0", "scale-150");
        }, Math.random() * 1000);

        setTimeout(() => {
            firework.remove();
        }, 3000 + Math.random() * 2000);
    }

    setTimeout(() => {
        fireworksContainer.remove();
    }, 5000);
}

function showSuccessMessage() {
    const messageDiv = document.createElement("div");
    messageDiv.className = `
        fixed inset-0 z-[10000] flex items-center justify-center 
        backdrop-blur-sm transition-all duration-1000
    `;
    messageDiv.innerHTML = `
        <div class="
            glass-morphism bg-white/10 border border-white/20
            rounded-2xl p-8 shadow-2xl transform 
            animate-jump-in animate-duration-500 animate-ease-out
        ">
            <div class="flex flex-col items-center space-y-4">
                <span class="
                    text-4xl text-emerald-400 animate-bounce 
                    animate-infinite animate-duration-1000
                ">✔</span>
                <p class="
                    text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 
                    bg-clip-text text-transparent tracking-wide
                    animate-pulse animate-duration-1000
                ">
                    Task Approved & Completed! 🎉
                </p>
            </div>
        </div>
    `;
    document.body.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.classList.add("opacity-0", "backdrop-blur-none");
        setTimeout(() => messageDiv.remove(), 1000);
    }, 5000);
}

// Add custom animations to head
const style = document.createElement('style');
style.textContent = `
    @keyframes sparkle {
        0% { transform: scale(1); opacity: 1; }
        100% { transform: scale(3); opacity: 0; }
    }
    .animate-sparkle { animation: sparkle 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
    
    .glass-morphism {
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
    }
`;
document.head.appendChild(style);


// RE-ASSIGN THE TASK
// RE-ASSIGN THE TASK
document.addEventListener("DOMContentLoaded", function () {
    const emailInput = document.getElementById("userEmail");
    const submitBtn = document.getElementById("submitReassignTask");

    const userFullName = document.getElementById("userFullName");
    const userStatus = document.getElementById("userStatus");
    const userProfilePicture = document.getElementById("userProfilePicture");
    const userTasks = document.getElementById("userTasks");
    const userCompletedTasks = document.getElementById("userCompletedTasks");
    const userCalpoints = document.getElementById("userCalpoints");
    const calAI = document.getElementById("calAI");

    // Set your variables dynamically from the template
    const ORG_ID = window.djangoData.orgId;
    const GROUP_ID = window.djangoData.groupId;
    const TASK_ID = window.djangoData.taskId;

    // Create a loading spinner (Tailwind-based)
    const spinner = document.createElement("span");
    spinner.className = "ml-2 animate-spin h-5 w-5 border-t-2 border-b-2 border-gray-500 hidden";
    submitBtn.appendChild(spinner); // Append spinner inside the button

    // Fetch user details in real-time
    emailInput.addEventListener("input", function () {
        const email = this.value.trim();
        if (email.length < 5) {
            userFullName.textContent = "-";
            userStatus.textContent = "-";
            userTasks.textContent = "-";
            userProfilePicture.style.display = "none";
            userCompletedTasks.textContent = "-";
            userCalpoints.textContent = "-";
            calAI.textContent = "-";
            submitBtn.disabled = true;
            return;
        }

        // Show loading state
        userStatus.textContent = "Checking...";
        submitBtn.disabled = true;

        fetch(`/tasks/fetch-user-info/${ORG_ID}/${GROUP_ID}/?email=${encodeURIComponent(email)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    userFullName.textContent = "Not Found!";
                    userStatus.textContent = data.error;
                    userProfilePicture.style.display = "none";
                    userTasks.style.display = 'none';
                    userCompletedTasks.style.display = 'none';
                    userCalpoints.style.display = "none";
                    calAI.style.display = "none";
                    submitBtn.disabled = true;
                } else {
                    userFullName.textContent = data.full_name;
                    userTasks.textContent = data.tasks;
                    userStatus.textContent = "Available in group";
                    userCompletedTasks.textContent = data.completed_tasks;
                    userCalpoints.textContent = data.calpoints;
                    calAI.textContent = data.final_message;
                    if (data.profile_picture) {
                        userProfilePicture.src = data.profile_picture;
                        userProfilePicture.style.display = "block";
                    } else {
                        userProfilePicture.style.display = "none";
                    }
                    submitBtn.disabled = false;
                }
            })
            .catch(error => {
                console.error("Error fetching user:", error);
            });
    });

    // Submit Reassignment Request
    submitBtn.addEventListener("click", function () {
        const email = emailInput.value.trim();
        if (!email) return;

        // Show spinner & disable button
        spinner.classList.remove("hidden");
        submitBtn.disabled = true;

        fetch(`/tasks/reassign-task/${ORG_ID}/${GROUP_ID}/${TASK_ID}/`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": getCSRFToken() },
            body: new URLSearchParams({ email: email })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            if (!data.error) new bootstrap.Modal(document.getElementById("reAssignmentTaskModal")).hide();
        })
        .catch(error => {
            console.error("Error reassigning task:", error);
        })
        .finally(() => {
            // Hide spinner & re-enable button after request completes
            spinner.classList.add("hidden");
            submitBtn.disabled = false;
        });
    });

    // Function to get CSRF Token from cookies (required for Django POST requests)
    function getCSRFToken() {
        const cookieValue = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
        return cookieValue ? cookieValue.split("=")[1] : "";
    }
});



// Manage the issues 
// Load Task Issues & Categorize Them
function loadTaskIssues() {
    const orgId = window.djangoData.orgId;
    const groupId = window.djangoData.groupId || null;
    const taskId = window.djangoData.taskId;

    if (!orgId || !taskId) {
        console.error("Missing orgId or taskId");
        return;
    }

    const issuesContainer = document.querySelector("#issuesContainer");
    issuesContainer.innerHTML = `<div class="text-center p-3"><div class="spinner-border text-primary"></div></div>`;

    // Open the modal
    const modal = new bootstrap.Modal(document.getElementById("issuesModal"));
    modal.show();

    fetch(`/tasks/fetch-task-issues/?org_id=${orgId}&group_id=${groupId}&task_id=${taskId}`)
        .then(response => response.json())
        .then(data => {
            window.issueData = data; // Store fetched issues for filtering
            filterIssues("open"); // Load Open issues by default
        })
        .catch(() => {
            issuesContainer.innerHTML = `<p class="text-danger text-center">Failed to load issues.</p>`;
        });
}

// Filter Issues Based on Selected Tab
function filterIssues(status) {
    if (!window.issueData) {
        console.error("Issue data not loaded yet!");
        return;
    }

    const issuesContainer = document.querySelector("#issuesContainer");
    const selectedIssues = window.issueData[status] || [];

    let content = selectedIssues
    .map(issue => `
        <div class="bg-white rounded-lg shadow-sm p-6 mb-4 border border-gray-100 hover:shadow-md transition-shadow">
            <div class="flex items-start justify-between gap-3 mb-3">
                <h3 class="font-semibold text-gray-900 text-base truncate">${issue.title}</h3>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    ${issue.priority}
                </span>
            </div>
            
            <p class="text-gray-600 text-sm mb-4 line-clamp-2">${issue.description}</p>
            
            <div class="flex items-center justify-between text-sm">
                <div class="text-gray-500">
                    <span class="inline-flex items-center">
                        <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                        </svg>
                        ${issue.reported_by}
                    </span>
                    <span class="mx-2">•</span>
                    <span>${issue.created_at}</span>
                </div>
                
                <button class="inline-flex items-center text-blue-600 hover:text-blue-800 transition-colors font-medium text-sm"
                    data-issue-id="${issue.id}" 
                    onclick="openIssueDiscussion(this)">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
                    </svg>
                    Discuss
                </button>
            </div>
        </div>
    `)
    .join("");
    issuesContainer.innerHTML = content || `<p class="text-muted text-center">No issues found in this category.</p>`;

    // Update active tab
    document.querySelectorAll("#issueTabs .nav-link").forEach(btn => btn.classList.remove("active"));
    document.querySelector(`#issueTabs [data-status='${status}']`).classList.add("active");
}


// Real time issues discussion
let issueFetchInterval = null; // Store interval reference
let lastMessageId = null; // Track last message ID for efficient fetching

function openIssueDiscussion(btn) {
    const orgId = window.djangoData.orgId;
    const groupId = window.djangoData.groupId || null;
    const taskId = window.djangoData.taskId;
    const issueId = btn.getAttribute("data-issue-id"); // Capture issue_id from button

    if (!orgId || !taskId || !issueId) {
        console.error("Missing parameters for issue discussion.");
        return;
    }

    const messagesContainer = document.getElementById("discussionMessages");
    messagesContainer.innerHTML = `<p class="text-muted text-center">Loading messages...</p>`;

    // Open modal
    const modal = new bootstrap.Modal(document.getElementById("issueDiscussionModal"));
    modal.show();

    // Store issueId globally for sending messages
    window.currentIssueId = issueId;
    lastMessageId = null; // Reset last message tracker

    // Fetch messages and start real-time updates
    fetchMessages();
    if (issueFetchInterval) clearInterval(issueFetchInterval); // Clear any existing interval
    issueFetchInterval = setInterval(fetchMessages, 2000); // Fetch new messages every 2 seconds
}

function fetchMessages() {
    const orgId = window.djangoData.orgId;
    const groupId = window.djangoData.groupId || null;
    const taskId = window.djangoData.taskId;
    const issueId = window.currentIssueId;

    if (!orgId || !taskId || !issueId) {
        console.error("Missing parameters for fetching messages.");
        return;
    }

    fetch(`/tasks/issue-discussion/${orgId}/${groupId}/${taskId}/${issueId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const messagesContainer = document.getElementById("discussionMessages");

                // If no new messages, return
                if (data.messages.length === 0 || (lastMessageId && lastMessageId === data.messages[data.messages.length - 1].id)) {
                    return;
                }

                messagesContainer.innerHTML = data.messages.map(msg => formatMessage(msg)).join("");
                lastMessageId = data.messages[data.messages.length - 1].id; // Update last seen message ID
                scrollToBottom(); // Auto-scroll to latest message
            } else {
                console.error("Failed to load messages.");
            }
        })
        .catch(() => console.error("Error fetching messages."));
}

function sendMessage() {
    const messageInput = document.getElementById("messageInput");
    const fileInput = document.getElementById("fileInput");

    const messageText = messageInput.value.trim();
    const file = fileInput.files[0];

    if (!messageText && !file) {
        alert("Enter a message or select a file.");
        return;
    }

    const formData = new FormData();
    formData.append("message", messageText);
    if (file) formData.append("file", file);

    fetch(`/tasks/issue-discussion/${window.djangoData.orgId}/${window.djangoData.groupId}/${window.djangoData.taskId}/${window.currentIssueId}/`, {
        method: "POST",
        body: formData,
        headers: { "X-CSRFToken": getCSRFToken() },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById("discussionMessages").innerHTML += formatMessage(data.message);
            messageInput.value = "";
            fileInput.value = "";
            scrollToBottom();
        } else {
            alert("Failed to send message.");
        }
    })
    .catch(() => alert("Error sending message."));
}

function formatMessage(msg) {
    const isMyMessage = msg.sender === window.djangoData.username;


    let filePreview = "";
    if (msg.files) {
        const fileType = getFileType(msg.files);
        filePreview = generateFilePreview(msg.files, fileType);
    }

    return `
    <div class="flex ${msg.sender === window.djangoData.username ? 'justify-end' : 'justify-start'} mb-4">
    ${msg.sender !== window.djangoData.username ? `
    <img src="${msg.sender_profile_pic || 'https://via.placeholder.com/40'}" 
         class="w-10 h-10 rounded-full mr-3 self-end border-2 border-white shadow-sm">` : ''}
    
    <div class="relative max-w-[80%] md:max-w-lg p-4 rounded-2xl ${msg.sender === window.djangoData.username ? 
        'bg-[#0084ff] text-white rounded-br-none ml-12' : 
        'bg-gray-100 text-gray-900 rounded-bl-none mr-12'} 
        shadow-sm hover:shadow-md transition-shadow duration-200">
        
        <div class="flex items-center gap-2 mb-1.5">
            ${msg.sender !== window.djangoData.username ? `
            <strong class="text-sm font-semibold">${msg.sender}</strong>` : ''}
            <small class="text-xs opacity-80">${msg.created_at}</small>
        </div>
        
        <p class="text-[15px] leading-snug font-[400]">${msg.message || ''}</p>
        
        ${filePreview ?
            `<div class="mt-3 border ${
                msg.sender === window.djangoData.username ? 'border-white/20' : 'border-gray-200'
            } rounded-xl overflow-hidden">
                ${filePreview}
            </div>` : ''
        }

        ${msg.sender === window.djangoData.username ? `
        <div class="absolute -right-2 bottom-0 w-4 h-4 overflow-hidden">
            <div class="absolute w-4 h-4 bg-[#0084ff] -rotate-45 transform origin-bottom-right"></div>
        </div>` : ''}
    </div>

    ${msg.sender === window.djangoData.username ? `
    <img src="${msg.sender_profile_pic || 'https://via.placeholder.com/40'}" 
         class="w-10 h-10 rounded-full ml-3 self-end border-2 border-white shadow-sm">` : ''}
</div>
`;



}

// Determine file type
function getFileType(fileUrl) {
    const ext = fileUrl.split('.').pop().toLowerCase();
    if (["png", "jpg", "jpeg", "gif", "bmp", "svg"].includes(ext)) return "image";
    if (["mp4", "webm", "ogg"].includes(ext)) return "video";
    if (["mp3", "wav", "ogg"].includes(ext)) return "audio";
    if (["pdf"].includes(ext)) return "pdf";
    return "other";
}

// Generate file preview with modal trigger
function generateFilePreview(fileUrl, fileType) {
    switch (fileType) {
        case "image":
            return `<img src="${fileUrl}" class="file-preview img-thumbnail" onclick="openFileModal('${fileUrl}', 'image')">`;
        case "video":
            return `<video class="file-preview" controls onclick="openFileModal('${fileUrl}', 'video')"><source src="${fileUrl}" type="video/mp4"></video>`;
        case "audio":
            return `<audio class="file-preview" controls><source src="${fileUrl}" type="audio/mpeg"></audio>`;
        case "pdf":
            return `<a href="${fileUrl}" class="file-preview" target="_blank" onclick="openFileModal('${fileUrl}', 'pdf')">📄 View PDF</a>`;
        default:
            return `<a href="${fileUrl}" class="file-preview" target="_blank">📎 Download File</a>`;
    }
}

// Open file preview modal
function openFileModal(fileUrl, fileType) {
    const modalBody = document.getElementById("filePreviewBody");
    let content = "";

    switch (fileType) {
        case "image":
            content = `<img src="${fileUrl}" class="img-fluid">`;
            break;
        case "video":
            content = `<video class="w-100" controls><source src="${fileUrl}" type="video/mp4"></video>`;
            break;
        case "pdf":
            content = `<iframe src="${fileUrl}" class="w-100" style="height: 500px;"></iframe>`;
            break;
        default:
            content = `<p class="text-muted">Cannot preview this file. <a href="${fileUrl}" target="_blank">Download here</a>.</p>`;
    }

    modalBody.innerHTML = content;
    new bootstrap.Modal(document.getElementById("filePreviewwModal")).show();
}

function scrollToBottom() {
    const messagesContainer = document.getElementById("discussionMessages");
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
}

// Stop fetching when modal closes
document.getElementById("issueDiscussionModal").addEventListener("hidden.bs.modal", () => {
    if (issueFetchInterval) clearInterval(issueFetchInterval);
});


// Filter msgs in real time
document.getElementById("messageSearch").addEventListener("input", function () {
    let query = this.value.toLowerCase().trim();
    let messagesContainer = document.getElementById("discussionMessages");

    if (!messagesContainer) {
        console.error("❌ Error: messagesContainer not found!");
        return;
    }

    let messages = messagesContainer.querySelectorAll(".flex.mb-4");

    if (messages.length === 0) {
        console.warn("⚠️ No messages found. Waiting for messages to load...");
        return;
    }

    console.log(`🔍 Searching for: "${query}"`);

    let matchCount = 0;

    messages.forEach((msg) => {
        let messageText = msg.querySelector("p")?.textContent.toLowerCase() || "";
        let senderName = msg.querySelector("strong")?.textContent.toLowerCase() || "";

        if (messageText.includes(query) || senderName.includes(query)) {
            msg.style.display = "flex";
            matchCount++;
        } else {
            msg.style.display = "none";
        }
    });

    console.log(`✅ Matches found: ${matchCount}`);
});

// Ensure messages are loaded before enabling search
function ensureMessagesLoaded() {
    let messagesContainer = document.getElementById("discussionMessages");

    if (!messagesContainer) {
        console.error("❌ Error: messagesContainer not found!");
        return;
    }

    let checkMessages = setInterval(() => {
        let messages = messagesContainer.querySelectorAll(".flex.mb-4");
        if (messages.length > 0) {
            console.log("✅ Messages loaded successfully. Search enabled.");
            clearInterval(checkMessages);
        }
    }, 500); // Check every 500ms
}

// Call this when opening the modal
ensureMessagesLoaded();


// Edit and manage task description
document.addEventListener("DOMContentLoaded", function () {
    const openBtn = document.getElementById("openTaskNewModal");
    const saveBtn = document.getElementById("saveTaskDescriptionNew");
    const taskDesc = document.getElementById("taskDescriptionNew");

    let orgId, groupId, taskId;

    // Open Modal & Fetch Description
    openBtn.addEventListener("click", function () {
        orgId = window.djangoData.orgId;
        groupId = window.djangoData.groupId;
        taskId = window.djangoData.taskId;

        fetch(`/tasks/manage-description/${orgId}/${groupId}/${taskId}/`)
            .then(response => response.json())
            .then(data => {
                taskDesc.value = data.description;
            })
            .catch(error => console.error("Error fetching task:", error));
    });

    // Save Updated Description
    saveBtn.addEventListener("click", function () {
        const newDescription = taskDesc.value.trim();

        if (!newDescription) {
            alert("Description cannot be empty!");
            return;
        }

        fetch(`/tasks/manage-description/${orgId}/${groupId}/${taskId}/`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `description=${encodeURIComponent(newDescription)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert("Task Updated Successfully!");
                const modal = bootstrap.Modal.getInstance(document.getElementById("DescriptionTaskNewModal"));
                modal.hide(); // Close the modal after saving
            }
        })
        .catch(error => console.error("Error updating task:", error));
    });
});


// Manage Project Plan
tinymce.init({
    selector: "#tiny-editor",
    menubar: true, // Full menu bar enabled
    plugins: [
        "advlist autolink lists link image charmap preview anchor",
        "searchreplace visualblocks visualchars code fullscreen",
        "insertdatetime media table paste help wordcount",
        "emoticons hr directionality textpattern codesample",
        "autosave quickbars nonbreaking pagebreak",
        "imagetools toc textcolor colorpicker",
        "spellchecker template print autoresize",
        "importcss advcode powerpaste tinydrive",
        "a11ychecker mentions casechange checklist",
        "permanentpen linkchecker",
        "fullscreen save hr",
        "bbcode emoticons accordion",
        "pageembed mediaembed insertdatetime",
        "export formatpainter noneditable",
        "autocorrect tinycomments footnotes typography"
    ],
    toolbar: [
        "undo redo | fontselect fontsizeselect formatselect",
        "bold italic underline strikethrough forecolor backcolor removeformat",
        "alignleft aligncenter alignright alignjustify",
        "bullist numlist checklist outdent indent",
        "link image media codesample insertdatetime table hr pagebreak",
        "searchreplace visualblocks visualchars spellchecker",
        "preview fullscreen print save code help",
        "charmap emoticons anchor toc",
        "casechange permanentpen template accordion",
        "autosave restoredraft importcss formatpainter",
        "export footnotes typography",
        "pageembed mediaembed tinycomments"
    ].join(" | "),
    
    // General Configurations
    height: 600,
    branding: false, // Remove TinyMCE branding
    contextmenu: "link image table", // Right-click options
    autoresize_bottom_margin: 50, // Auto resize support
    quickbars_insert_toolbar: "quicktable image media pageembed",
    quickbars_selection_toolbar: "bold italic | quicklink h2 h3 blockquote",
    toolbar_mode: "sliding", // Responsive toolbar
    content_style: "body { font-family: Arial, sans-serif; font-size: 14px; }",

    // Image & Media Upload
    image_title: true,
    automatic_uploads: true,
    file_picker_types: "image media file",
    file_picker_callback: function(cb, value, meta) {
        var input = document.createElement("input");
        input.setAttribute("type", "file");
        if (meta.filetype === "image") {
            input.setAttribute("accept", "image/*");
        } else if (meta.filetype === "media") {
            input.setAttribute("accept", "video/*,audio/*");
        } else {
            input.setAttribute("accept", "*");
        }
        input.onchange = function() {
            var file = this.files[0];
            var reader = new FileReader();
            reader.onload = function() {
                cb(reader.result, { title: file.name });
            };
            reader.readAsDataURL(file);
        };
        input.click();
    },

    // Spellchecker
    spellchecker_language: "en",
    spellchecker_dialog: true,

    // File Manager & Drive Integration
    file_picker_callback: function(callback, value, meta) {
        var input = document.createElement("input");
        input.setAttribute("type", "file");
        input.onchange = function() {
            var file = this.files[0];
            var reader = new FileReader();
            reader.onload = function() {
                callback(reader.result, { title: file.name });
            };
            reader.readAsDataURL(file);
        };
        input.click();
    },

    // Table Configuration
    table_toolbar: "tableprops cell row column deletetable",
    
    // Autosave Configuration
    autosave_interval: "30s",
    autosave_restore_when_empty: true,
    autosave_retention: "2m",

    // Export as PDF, DOCX, etc.
    export_formats: "pdf docx xlsx",
    export_background: true,

    // Accessibility
    a11ychecker_html_version: "html5",

    // Commenting System
    tinycomments_mode: "embedded",
    tinycomments_author: "Author Name"
});



// Function to get the dynamic task ID
function getTaskId() {
    return window.djangoData && window.djangoData.taskId ? window.djangoData.taskId : null;
}

// Open Modal & Fetch Data via AJAX
document.getElementById("openProjectPlanModal").addEventListener("click", function () {
    let taskId = getTaskId();
    if (!taskId) {
        alert("Error: Task ID not found!");
        return;
    }
    
    fetchProjectPlan(taskId);
    new bootstrap.Modal(document.getElementById("projectPlanModal")).show();
});

// Fetch Project Plan via AJAX
function fetchProjectPlan(taskId) {
    fetch(`/tasks/project-plan/${taskId}/`)
        .then(response => response.json())
        .then(data => tinymce.get("tiny-editor").setContent(data.project_plan || ""))  // 🔥 FIXED: Set empty content if null
        .catch(error => console.error("Error fetching project plan:", error));
}

// Save Project Plan via AJAX
document.getElementById("saveProjectPlanBtn").addEventListener("click", function () {
    let taskId = getTaskId();
    if (!taskId) {
        alert("Error: Task ID not found!");
        return;
    }

    let content = tinymce.get("tiny-editor").getContent();

    fetch(`/tasks/project-plan/${taskId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: `project_plan=${encodeURIComponent(content)}`,
    })
    .then(response => response.json())
    .then(data => {
        alert("Project Plan Updated!");
        new bootstrap.Modal(document.getElementById("projectPlanModal")).hide();
    })
    .catch(error => console.error("Error updating project plan:", error));
});

// CSRF Token Helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}