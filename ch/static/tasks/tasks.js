
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
            matches = highlightMatches(searchText);
            updateCounter();
        } else {
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
    });
});