


// Help Command

// Add animation when modal is shown (Whois)
  document.getElementById('WhoiseModal').addEventListener('show.bs.modal', function () {
    this.querySelector('.modal-content').classList.add('animate-in');
});

// Add closing animation
document.getElementById('closeWhoiseModal').addEventListener('click', function() {
    const modal = document.getElementById('WhoiseModal');
    modal.querySelector('.modal-content').classList.add('animate-out');
    setTimeout(() => modal.classList.remove('show'), 300);
});


// Show all commands     
document.addEventListener('DOMContentLoaded', function() {
const inputField = document.getElementById("chat-message-input");
const modal = document.getElementById("commandsModal");
const closeModal = document.getElementById("closeCommandsModal");
const commandItems = document.querySelectorAll('.group'); // Selecting command items

// Show the modal if the input is "/help"
inputField.addEventListener('input', function() {
    if (inputField.value.trim() === '/help') {
        modal.classList.remove('hidden'); // Show modal when "/help" is typed
    }
});

// Close the modal
closeModal.addEventListener('click', function() {
    modal.classList.add('hidden');
    inputField.value = ''; // Clear input after closing the modal
});

// When a command is selected from the modal
commandItems.forEach(item => {
    item.addEventListener('click', function() {
        inputField.value = ''; // Clear existing input
        const selectedCommand = item.querySelector('p').textContent.split(' ')[0]; // Get the command part
        inputField.value += selectedCommand + " "; // Append the selected command to the input
        modal.classList.add('hidden'); // Close the modal after selecting the command
    });
});
});

// ---------------------------------------------------------------------------------------------------------------------------
// /PROFILE COMMAND TO SHOW USERS PROFILE
document.addEventListener('DOMContentLoaded', function() {
const inputField = document.getElementById("chat-message-input");
const modal = document.getElementById("profileModal");
const closeModal = document.getElementById("closeProfileModal");

inputField.addEventListener('input', function() {
    if (inputField.value.trim() === '/profile') {
        fetchProfileData(); // Fetch user profile details
        modal.classList.remove('hidden');
    }
});

closeModal.addEventListener('click', function() {
    modal.classList.add('hidden');
});

function fetchProfileData() {
    // Assuming org_id is available and profile info can be fetched from a Django view
    const orgId = window.djangoData.orgId; // Replace with actual org ID
    fetch(`/dm/profile/${orgId}/`)  // Your Django URL that handles this request
        .then(response => response.json())
        .then(data => {
            document.getElementById('profileFullName').textContent = data.full_name;
            document.getElementById('profileRole').textContent = data.role; 
            document.getElementById('profileOrgName').textContent = data.organization;
            document.getElementById('profileLastLogin').textContent = `Last login: ${data.last_login}`;

            // Set profile picture if available
            const profilePicUrl = data.profile_picture.url? `/media/${data.profile_picture} ` : '';
            document.getElementById('profilePicture').src = profilePicUrl;
        })
        .catch(error => console.error('Error fetching profile data:', error));
}
});



// /WHOISE IMPLEMENTATION
document.addEventListener('DOMContentLoaded', function () {
const inputField = document.getElementById("chat-message-input");
const modal = new bootstrap.Modal(document.getElementById('WhoiseModal')); // Bootstrap modal initialization
const closeModal = document.getElementById("closeWhoiseModal");

inputField.addEventListener('input', function () {
    if (inputField.value.trim() === '/whois') {
        const otherUserId = window.djangoData.otherUserId;  // Getting from template
        const orgId = window.djangoData.orgId;      // Organization ID
        const conversationId = window.djangoData.conversationId; // Conversation ID
        
        fetchWhoisData(orgId, otherUserId, conversationId); // Fetch user details
        modal.show(); // This will open the modal using Bootstrap's method
    }
});

closeModal.addEventListener('click', function () {
    modal.hide(); // Hide the modal using Bootstrap's method
});

function fetchWhoisData(orgId, otherUserId, conversationId) {
    fetch(`/dm/dm/whois/${orgId}/${otherUserId}/${conversationId}/`)  // Django URL for fetching user data
        .then(response => response.json())
        .then(data => {
            document.getElementById('whoisFullName').textContent = data.full_name;
            document.getElementById('whoisRole').textContent = data.role;
            document.getElementById('whoisOrgName').textContent = data.organization;
            document.getElementById('whoisMeetingCount').textContent = `Total Meetings: ${data.total_meetings}`;

            // Display upcoming meetings
            const meetingsContainer = document.getElementById('whoisUpcomingMeetings');
            meetingsContainer.innerHTML = ""; // Clear previous content
            if (data.upcoming_meetings.length > 0) {
                data.upcoming_meetings.forEach(meeting => {
                    const meetingItem = document.createElement('li');
                    meetingItem.textContent = `${meeting.meeting_title} on ${meeting.meeting_date} at ${meeting.start_time}`;
                    meetingsContainer.appendChild(meetingItem);
                });
            } else {
                meetingsContainer.innerHTML = "<li>No upcoming meetings</li>";
            }

            // Set profile picture from the response directly
            const profilePic = document.getElementById('whoisProfilePicture');
            if (data.profile_picture) {
                profilePic.src = data.profile_picture; // Use the URL from the response
                profilePic.classList.remove('hidden'); // Ensure it's visible
            } else {
                profilePic.classList.add('hidden'); // Hide if no picture
            }
        })
        .catch(error => console.error('Error fetching whois data:', error));
}
});


// RECENT IMPLEMENTATION
document.addEventListener('DOMContentLoaded', function () {
const inputField = document.getElementById("chat-message-input");
const modal = new bootstrap.Modal(document.getElementById("RecentModal"));
const closeModal = document.getElementById("closeRecentModal");

// Event listener for user input in the message input field
inputField.addEventListener('input', function () {
    const command = inputField.value.trim();

    // Only trigger if the command starts with '/recent' and contains a valid type at the end
    if (command.startsWith('/recent') && command.split(' ').length === 2) {
        const parts = command.split(' ');
        const type = parts[1]; // The second word after '/recent': 'code', 'message', or 'files'

        // Validate that type is one of the valid types
        if (['code', 'message', 'files'].includes(type)) {
            // Get dynamic data from your template context
            const otherUserId = window.djangoData.otherUserId;  // Get user ID dynamically
            const orgId =window.djangoData.orgId;      // Get organization ID dynamically
            const conversationId = window.djangoData.conversationId; // Get conversation ID dynamically

            // Fetch the recent data based on the type
            fetchRecentData(orgId, otherUserId, conversationId, type);
            modal.show(); // Show the modal using Bootstrap's method
        }
    }
});

// Close modal when the close button is clicked
closeModal.addEventListener('click', function () {
    modal.hide(); // Hide the modal
});

// Function to fetch recent data based on the type
function fetchRecentData(orgId, otherUserId, conversationId, type) {
    // Construct URL for the API endpoint
    const url = `/dm/recent/${orgId}/${otherUserId}/${conversationId}/${type}/`;

    // Fetch data from the server
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const recentContainer = modal._element.querySelector('#recentDataList');
            if (!recentContainer) {
                console.error("Recent content container not found in the modal.");
                return; // Exit if there's no container for recent data
            }

            recentContainer.innerHTML = ''; // Clear previous content

            if (data.recent_data && data.recent_data.length > 0) {
                data.recent_data.forEach(item => {
                    const itemElement = document.createElement('li');
                    const timestamp = new Date(item.timestamp).toLocaleString();

                    // Render data based on the type
                    if (type === 'code') {
                        itemElement.classList.add('material-card', 'code-snippet');
                        itemElement.innerHTML = `
                            <div class="card">
                                <div class="card-body">
                                    <p><strong>Code Snippet:</strong></p>
                                    <pre><code class="language-javascript">${item.code_snippet}</code></pre>
                                    <p><small>Sent at: ${timestamp}</small></p>
                                </div>
                            </div>
                        `;
                        recentContainer.appendChild(itemElement);

                        // Apply syntax highlighting for the code snippet
                        Prism.highlightAll();
                    } else if (type === 'message') {
                        itemElement.classList.add('material-card', 'message');
                        itemElement.innerHTML = `
                            <div class="card">
                                <div class="card-body">
                                    <p><strong>Message:</strong> ${item.text}</p>
                                    <p><small>Sent at: ${timestamp}</small></p>
                                </div>
                            </div>
                        `;
                        recentContainer.appendChild(itemElement);
                    } else if (type === 'files') {
                        itemElement.classList.add('material-card', 'file-preview');
                        const fileUrl = `/media/${item.file_url}`; // Ensure correct file URL
                        const fileExtension = item.file_url.split('.').pop().toLowerCase();

                        let filePreviewContent = '';
                        if (['jpg', 'jpeg', 'png', 'gif'].includes(fileExtension)) {
                            // Image preview
                            filePreviewContent = `
                                <img src="${fileUrl}" alt="Image Preview" style="max-width: 100%; border-radius: 8px;" />
                            `;
                        } else if (fileExtension === 'pdf') {
                            // Embed PDF preview
                            filePreviewContent = `
                                <iframe src="${fileUrl}" style="width: 100%; height: 300px; border-radius: 8px;"></iframe>
                            `;
                        } else if (['mp4', 'webm', 'ogg'].includes(fileExtension)) {
                            // Video preview
                            filePreviewContent = `
                                <video src="${fileUrl}" controls style="max-width: 100%; border-radius: 8px;"></video>
                            `;
                        } else if (['mp3', 'wav', 'ogg'].includes(fileExtension)) {
                            // Audio preview
                            filePreviewContent = `
                                <audio src="${fileUrl}" controls style="border-radius: 8px;"></audio>
                            `;
                        } else {
                            // Provide download link for other file types
                            filePreviewContent = `
                                <a href="${fileUrl}" download style="color: #007bff;">Download file: ${item.file_url}</a>
                            `;
                        }

                        itemElement.innerHTML = `
                            <div class="card">
                                <div class="card-body">
                                    <p><strong>File:</strong></p>
                                    ${filePreviewContent}
                                    <p><small>Sent at: ${timestamp}</small></p>
                                </div>
                            </div>
                        `;
                        recentContainer.appendChild(itemElement);
                    }
                });
            } else {
                recentContainer.innerHTML = "<li>No recent data available.</li>";
            }
        })
        .catch(error => {
            console.error('Error fetching recent data:', error);
            alert('Failed to load recent data.');
        });
}
});

