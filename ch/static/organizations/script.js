
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


// ACCOUNTS & PROFILE

document.addEventListener("DOMContentLoaded", function () {
    const orgId = "{{ organization.id }}";  // Organization ID (pass dynamically)

    // Fetch the current profile data when the modal opens
    const editProfileModal = document.getElementById("editProfileModal");
    editProfileModal.addEventListener("show.bs.modal", async function () {
        // Send a GET request to fetch the user's current profile data
        const response = await fetch(`/organizations/modify-profile/${organizationId}/`);
        const data = await response.json();

        if (data.success) {
            // Populate the form with existing profile data
            document.getElementById("full_name").value = data.data.full_name || '';
            document.getElementById("email").value = data.data.email || '';
            
            // Show the profile picture if it exists
            const profilePictureImg = document.getElementById("profile_picture_img");
            if (data.data.profile_picture) {
                profilePictureImg.src = data.data.profile_picture;
                document.getElementById("profile_picture_preview").style.display = "block"; // Show preview
            } else {
                document.getElementById("profile_picture_preview").style.display = "none"; // Hide preview if no picture
            }
        } else {
            alert(data.error || "Error loading profile data.");
        }
    });

    // Handle the form submission to update the profile
    const editProfileForm = document.getElementById("editProfileForm");
    editProfileForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const fullName = document.getElementById("full_name").value;
        const email = document.getElementById("email").value;
        const profilePicture = document.getElementById("profile_picture").files[0];

        const formData = new FormData();
        formData.append("full_name", fullName);
        formData.append("email", email);
        if (profilePicture) {
            formData.append("profile_picture", profilePicture);
        }

        const response = await fetch(`/organizations/modify-profile/${organizationId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
            },
            body: formData,
        });

        const data = await response.json();
        if (data.success) {
            alert(data.message);
            location.reload(); // Reload the page to reflect changes
            document.getElementById("editProfileModal").querySelector(".btn-close").click(); // Close modal
        } else {
            alert(data.error || "Error updating profile.");
        }
    });

    // Function to get CSRF token from the cookies
    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1];
    }
});


// HIDE ORGANIZATION 

// WORKSPACE STATUS BUTTONS FEATURES
document.querySelectorAll('.status-pill').forEach(button => {
    button.addEventListener('click', function() {
        document.querySelectorAll('.status-pill').forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
        document.getElementById('statusSelect').value = this.dataset.value;
    });
});



