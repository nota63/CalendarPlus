


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


// /JOKES (RETURN PYJOKES)

// /JOKES (RETURN PYJOKES)
document.addEventListener('DOMContentLoaded', function () {
    const inputField = document.getElementById("chat-message-input");
    const modal = new bootstrap.Modal(document.getElementById("jokeModal"));
    const jokeList = document.getElementById("jokeList");

    // Event listener for user input in the message input field
    inputField.addEventListener('input', function () {
        const command = inputField.value.trim();

        // Trigger if the command starts with '/joke'
        if (command.startsWith('/joke')) {
            fetchJokes();  // Fetch jokes from the server and display in modal
            modal.show();  // Show the modal using Bootstrap's method
        }
    });

    // Function to fetch jokes from the server
    function fetchJokes() {
        fetch('/dm/jokes/')
            .then(response => response.json())
            .then(data => {
                const jokes = data.jokes;
                jokeList.innerHTML = ''; // Clear previous jokes
                
                // Add jokes to the modal
                jokes.forEach(joke => {
                    const jokeItem = document.createElement('li');
                    jokeItem.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center', 'joke-item');
                    jokeItem.innerHTML = `
                        <span class="joke-text">${joke.joke}</span>
                        <button class="btn btn-sm btn-outline-primary select-joke">Select</button>
                    `;
                    
                    // Add click event listener to each joke
                    jokeItem.querySelector('.select-joke').addEventListener('click', function () {
                        inputField.value = joke.joke;  // Append the selected joke to the input field
                        modal.hide();  // Close the modal
                    });

                    jokeList.appendChild(jokeItem);
                });
            })
            .catch(error => {
                console.error('Error fetching jokes:', error);
                alert('Failed to load jokes.');
            });
    }
});


// TENOR API AND GIFS
document.addEventListener('DOMContentLoaded', function () {
    const inputField = document.getElementById("chat-message-input");
    const modal = new bootstrap.Modal(document.getElementById("gifModal"));
    const gifList = document.getElementById("gifList");

    // Event listener for user input in the message input field
    inputField.addEventListener('input', function () {
        const command = inputField.value.trim();

        // Trigger if the command starts with '/gif'
        if (command.startsWith('/gif')) {
            const keyword = command.split(' ')[1];  // Get the keyword after '/gif'
            if (keyword) {
                fetchGifs(keyword);  // Fetch GIFs based on the keyword
                modal.show();  // Show the modal using Bootstrap's method
            }
        }
    });

    // Function to fetch GIFs from the Tenor API
    function fetchGifs(keyword) {
        fetch(`/dm/gifs/?query=${keyword}`)
            .then(response => response.json())
            .then(data => {
                const gifs = data.gifs;
                gifList.innerHTML = ''; // Clear previous GIFs
                
                if (gifs && gifs.length > 0) {
                    // Add GIFs to the modal
                    gifs.forEach(gif => {
                        const gifItem = document.createElement('li');
                        gifItem.classList.add('list-group-item', 'flex', 'flex-col', 'justify-start', 'items-center', 'p-4', 'm-4', 'rounded-xl', 'bg-white', 'border', 'border-gray-300', 'shadow-lg', 'cursor-pointer', 'transition-all', 'hover:bg-gray-100', 'hover:scale-105', 'hover:shadow-2xl', 'duration-300', 'w-full', 'max-w-xs');

                        const img = document.createElement('img');
                        img.src = gif.media[0].gif.url;
                        img.alt = 'GIF';
                        img.classList.add('w-full', 'h-64', 'object-cover', 'rounded-lg', 'transition-all', 'hover:scale-110', 'duration-300');  // High quality and zoom effect on hover

                        gifItem.appendChild(img);

                        // Add click event listener to each GIF
                        gifItem.addEventListener('click', function () {
                            inputField.value = gif.media[0].gif.url;  // Append the selected GIF URL to the input field
                            modal.hide();  // Close the modal
                        });

                        gifList.appendChild(gifItem);
                    });
                } else {
                    gifList.innerHTML = "<li class='text-center text-gray-500'>No GIFs found.</li>";
                }
            })
            .catch(error => {
                console.error('Error fetching GIFs:', error);
                alert('Failed to load GIFs.');
            });
    }
});


// SCHEDULE MESSAGE COMMAND

document.addEventListener('DOMContentLoaded', function () {
    const inputField = document.getElementById("chat-message-input");
    let scheduleTime = '';  // Store the time entered by the user
    let message = '';  // Store the message entered by the user
    let typingTimer;  // Variable to hold the timer reference
    const doneTypingInterval = 2000;  // Delay time (2 seconds)

    // Event listener for user input in the message input field
    inputField.addEventListener('input', function () {
        const command = inputField.value.trim();

        // Check if the command starts with '/schedule'
        if (command.startsWith('/schedule')) {
            const parts = command.split(' ', 3);  // Split input into date/time and message
            if (parts.length >= 3) {
                // Time and message parts
                scheduleTime = parts[1];  // Time part
                message = parts.slice(2).join(' ');  // The message part

                // If the time doesn't include hours and minutes, append "00:00:00" as default
                if (!scheduleTime.includes(':')) {
                    scheduleTime += " 00:00:00";  // Default to midnight if no time is provided
                }

                // If both time and message are entered, reset the timer
                if (scheduleTime && message) {
                    clearTimeout(typingTimer);

                    // Start the timer to delay the request (2 seconds after the user finishes typing)
                    typingTimer = setTimeout(function () {
                        // Get the org_id and conversation_id from the page
                        const orgId = window.djangoData.orgId;  
                        const conversationId = window.djangoData.conversationId;

                        if (!orgId || !conversationId) {
                            alert('Organization or Conversation ID is missing.');
                            return;
                        }

                        // Construct the scheduling URL
                        const url = `/dm/schedule_message_command/${orgId}/${conversationId}/`;

                        // Send the schedule request to the server via POST
                        fetch(url, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                            },
                            body: new URLSearchParams({
                                message: message,
                                schedule_time: scheduleTime,
                                schedule_type: 'specific_time',  // Default to 'specific_time'
                            })
                        })
                            .then(response => response.json())
                            .then(data => {
                                if (data.status === 'success') {
                                    alert('Message scheduled successfully!');
                                    inputField.value = '';  // Clear input after successful scheduling
                                } else {
                                    alert('Error scheduling message: ' + data.message);
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                alert('An error occurred while scheduling the message.');
                            });
                    }, doneTypingInterval);  // 2 seconds delay before making the request
                }
            } else {
                alert('Please provide the date, time, and message.');
            }
        }
    });
});


// /TODO COMMAND
document.addEventListener('DOMContentLoaded', function () {
    const inputField = document.getElementById("chat-message-input");
    let dueDate = '';  
    let todoText = '';  
    let typingTimer;  
    const doneTypingInterval = 2000;  

    // Create a spinner
    const spinner = document.createElement('div');
    spinner.innerHTML = `<div class="mui-spinner"></div>`;
    spinner.style.display = "none"; // Initially hidden
    document.body.appendChild(spinner);

    // Create a pop-up container
    const popup = document.createElement('div');
    popup.classList.add('todo-popup');
    popup.style.display = "none"; // Initially hidden
    document.body.appendChild(popup);

    function getCSRFToken() {
        let csrfToken = null;
        document.cookie.split(';').forEach(cookie => {
            let [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                csrfToken = value;
            }
        });
        return csrfToken;
    }

    inputField.addEventListener('input', function () {
        const command = inputField.value.trim();
        if (command.startsWith('/todo')) {
            const parts = command.split(' ');  
            if (parts.length >= 3) {
                dueDate = parts[1] + (parts.length >= 4 ? ` ${parts[2]}` : " 00:00:00");  
                todoText = parts.slice(3).join(' ');  

                if (dueDate && todoText) {
                    clearTimeout(typingTimer);
                    typingTimer = setTimeout(function () {
                        const orgId = window.djangoData.orgId;  
                        const conversationId = window.djangoData.conversationId;
                        if (!orgId || !conversationId) {
                            alert('Organization or Conversation ID is missing.');
                            return;
                        }

                        const url = `/dm/schedule_todo_command/${orgId}/${conversationId}/`;

                        // Show spinner
                        spinner.style.display = "flex";

                        fetch(url, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'X-CSRFToken': getCSRFToken(),
                            },
                            body: new URLSearchParams({
                                todo: todoText,
                                due_date: dueDate,
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            spinner.style.display = "none"; // Hide spinner

                            if (data.status === 'success') {
                                showPopup(todoText, dueDate, "task", "medium"); // Show popup
                                inputField.value = '';  
                            } else {
                                alert('Error saving todo: ' + data.message);
                            }
                        })
                        .catch(error => {
                            spinner.style.display = "none"; 
                            console.error('Error:', error);
                            alert('An error occurred while saving the todo.');
                        });
                    }, doneTypingInterval);
                }
            }
        }
    });

    function showPopup(todo, dueDate, type, priority) {
        popup.innerHTML = `
            <div class="popup-content">
                <span class="mui-icon">📌</span> <strong>Task:</strong> ${todo} <br>
                <span class="mui-icon">⏳</span> <strong>Due:</strong> ${dueDate} <br>
                <span class="mui-icon">📂</span> <strong>Type:</strong> ${type} <br>
                <span class="mui-icon">⚡</span> <strong>Priority:</strong> ${priority}
            </div>
        `;
        popup.style.display = "block";
        setTimeout(() => popup.style.display = "none", 8000); // Hide after 5s
    }
});
