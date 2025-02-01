
// Update Workspace Icon
document.addEventListener("DOMContentLoaded", function () {
    const updateIconForm = document.getElementById("updateIconForm");

    updateIconForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const orgId = "{{ organization.id }}"; 
        const iconInput = document.getElementById("workspaceIcon");
        const formData = new FormData();
        formData.append("icon", iconInput.files[0]);

        const response = await fetch(`/organizations/workspace-icon/${organizationId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
            },
            body: formData,
        });

        const data = await response.json();
        if (data.success) {
            alert("Workspace icon updated successfully!");
            document.getElementById("currentIcon").src = data.icon_url;
            iconInput.value = ""; // Reset file input
        } else {
            alert(data.error);
        }
    });

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1];
    }
});



// UPDATE WORKSPACE STATUS
document.addEventListener("DOMContentLoaded", function () {
    const updateStatusForm = document.getElementById("updateStatusForm");

    updateStatusForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const orgId = "{{ organization.id }}"; // Organization ID (Pass dynamically)
        const selectedStatus = document.getElementById("statusSelect").value;

        const data = {
            status: selectedStatus
        };

        const response = await fetch(`/organizations/workspace-status/${organizationId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",  // Set the correct content type
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify(data),  // Send the data as JSON
        });

        const responseData = await response.json();
        if (responseData.success) {
            alert("Organization status updated successfully!");
            document.getElementById("updateStatusModal").querySelector(".btn-close").click(); // Close modal
        } else {
            alert(responseData.error);
        }
    });

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1];
    }
});




