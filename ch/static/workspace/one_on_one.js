


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





// /todo manage (MANAGE USER TODOS)
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    const modal = document.getElementById("todoManageModal");
    const closeModal = document.getElementById("closeTodoModal");
    const todoContainer = document.getElementById("todoContainer");
    const messageContainer = document.getElementById("messageContainer"); // Container to show messages
    const ctx = document.getElementById("todoChart").getContext("2d");
    let todoChart; // Chart reference
    let isFetching = false; // To prevent multiple fetches

    // Function to get CSRF token
    function getCSRFToken() {
        let csrfToken = null;
        document.cookie.split(";").forEach(cookie => {
            let [name, value] = cookie.trim().split("=");
            if (name === "csrftoken") {
                csrfToken = value;
            }
        });
        return csrfToken;
    }

    // Fetch Todos from backend with smooth transition
    function fetchTodos() {
        if (isFetching) return; // Prevent multiple fetch calls simultaneously
        isFetching = true;

        const orgId = window.djangoData.orgId;
        const conversationId = window.djangoData.conversationId;

        if (!orgId || !conversationId) {
            alert("Organization or Conversation ID is missing.");
            isFetching = false;
            return;
        }

        fetch(`/dm/manage_todo/${orgId}/${conversationId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    populateTodos(data.todos);
                    updateChart(data.todo_counts); // Pass counts for chart update
                } else {
                    alert("Error fetching todos: " + data.message);
                }
                isFetching = false;
            })
            .catch(error => {
                console.error("Error fetching todos:", error);
                alert("An error occurred while fetching todos.");
                isFetching = false;
            });
    }

    // Populate Todos in Modal with smooth transitions
    // Populate Todos in Modal with smooth transitions
    function populateTodos(todos) {
        todoContainer.innerHTML = ""; // Clear previous todos
        todos.forEach(todo => {
            const todoElement = document.createElement("div");
            todoElement.classList.add("todo-item");
            todoElement.innerHTML = `
                <div class="todo-details">
                    <p><strong>${todo.todo}</strong></p>
                    <p>Type: <select data-id="${todo.id}" class="todo-type">
                        <option value="meeting" ${todo.type === "meeting" ? "selected" : ""}>Meeting</option>
                        <option value="task" ${todo.type === "task" ? "selected" : ""}>Task</option>
                        <option value="reminder" ${todo.type === "reminder" ? "selected" : ""}>Reminder</option>
                    </select></p>
                    <p>Priority: <select data-id="${todo.id}" class="todo-priority">
                        <option value="low" ${todo.priority === "low" ? "selected" : ""}>Low</option>
                        <option value="medium" ${todo.priority === "medium" ? "selected" : ""}>Medium</option>
                        <option value="high" ${todo.priority === "high" ? "selected" : ""}>High</option>
                        <option value="urgent" ${todo.priority === "urgent" ? "selected" : ""}>Urgent</option>
                    </select></p>
                    <p>Reminder: <select data-id="${todo.id}" class="todo-reminder">
                        <option value="Before 10 minutes" ${todo.reminder === "Before 10 minutes" ? "selected" : ""}>Before 10 minutes</option>
                        <option value="Before 20 minutes" ${todo.reminder === "Before 20 minutes" ? "selected" : ""}>Before 20 minutes</option>
                        <option value="Before an hour" ${todo.reminder === "Before an hour" ? "selected" : ""}>Before an hour</option>
                        <option value="None" ${todo.reminder === "None" ? "selected" : ""}>None</option>
                    </select></p>
                    <p>Status: <select data-id="${todo.id}" class="todo-status">
                        <option value="pending" ${todo.status === "pending" ? "selected" : ""}>Pending</option>
                        <option value="in_progress" ${todo.status === "in_progress" ? "selected" : ""}>In Progress</option>
                        <option value="completed" ${todo.status === "completed" ? "selected" : ""}>Completed</option>
                         <p>Due Date: <input type="datetime-local" value="${todo.due_date}" class="todo-due-date" data-id="${todo.id}" /></p>
                    </select></p>
                </div>
                <button class="delete-todo" data-id="${todo.id}">🗑️ Delete</button>
            `;
            todoContainer.appendChild(todoElement);
        });

        attachEventListeners(); // Attach event listeners for updates and deletion
    }




    // Update Chart with smooth transitions
    function updateChart(todoCounts) {
        if (todoChart) {
            todoChart.destroy();
        }
        todoChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: ["Pending", "In Progress", "Completed"],
                datasets: [{
                    label: "Todo Status Count",
                    data: [todoCounts.pending, todoCounts.in_progress, todoCounts.completed],
                    backgroundColor: ["#f39c12", "#3498db", "#2ecc71"]
                }]
            },
            options: {
                animation: {
                    duration: 1000, // Smooth transition for chart updates
                    easing: "easeInOutQuart"
                }
            }
        });
    }

    // Event Listeners for Todo Updates & Deletion
    function attachEventListeners() {
        document.querySelectorAll(".todo-type, .todo-priority, .todo-reminder, .todo-status").forEach(select => {
            select.addEventListener("change", function () {
                const todoId = this.dataset.id;
                const field = this.className.split("-")[1];
                const value = this.value;
                updateTodo(todoId, field, value);
            });
        });

        document.querySelectorAll(".delete-todo").forEach(button => {
            button.addEventListener("click", function () {
                const todoId = this.dataset.id;
                deleteTodo(todoId);
            });
        });
    }

    // Update Todo (Handle via backend with smooth transitions)
    function updateTodo(todoId, field, value) {
        const orgId = window.djangoData.orgId;
        const conversationId = window.djangoData.conversationId;
    
        fetch(`/dm/manage_todo/update/${orgId}/${conversationId}/${todoId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",  // Change this to application/json
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                [field]: value                   // Ensure the data is sent as a JSON object
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                showMessage("Todo updated successfully!", "success");
            } else {
                showMessage("Error updating todo: " + data.message, "error");
            }
        })
        .catch(error => showMessage("Error updating todo: " + error, "error"));
    }

    // Delete Todo with smooth transitions
    function deleteTodo(todoId) {
        const orgId = window.djangoData.orgId;
        const conversationId = window.djangoData.conversationId;

        fetch(`/dm/manage_todo/delete/${orgId}/${conversationId}/${todoId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken()
            },
            body: new URLSearchParams({ todo_id: todoId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                fetchTodos(); // Refresh todos after delete
                showMessage("Todo deleted successfully!", "success");
            } else {
                showMessage("Error deleting todo: " + data.message, "error");
            }
        })
        .catch(error => showMessage("Error deleting todo: " + error, "error"));
    }

    // Show success/error message
    function showMessage(message, type) {
        messageContainer.innerHTML = `<div class="message ${type}">${message}</div>`;
        setTimeout(() => {
            messageContainer.innerHTML = ''; // Hide the message after 3 seconds
        }, 3000);
    }

    // Open Modal When "/todo manage" is typed
    inputField.addEventListener("input", function () {
        if (inputField.value.trim() === "/todo manage") {
            inputField.value = ""; // Clear input
            modal.style.display = "block"; // Show modal
            fetchTodos(); // Fetch todos
        }
    });

    // Close Modal
    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
    });

    // Close Modal when clicking outside
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});


// /GREET 

document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");

    inputField.addEventListener("input", function () {
        if (inputField.value.trim() === "/greet") {
            setTimeout(() => {
                inputField.value = "Hello there! 😊 I hope you're having a fantastic day! How can I assist you today? Whether it's managing tasks, scheduling reminders, or just chatting, I'm here to help! 💡";
            }, 100); // Adding a small delay for better UX
        }
    });
});


// /MEME (GENERATES RANDOM MEME FROM MEME API)
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    const memeModal = document.createElement("div");
    const memeBox = document.createElement("div");
    const memeImage = document.createElement("img");
    const selectMemeButton = document.createElement("button");
    const closeMemeButton = document.createElement("span");
    const loader = document.createElement("div");

    // Apply styles to the modal (Material UI look)
    Object.assign(memeModal.style, {
        position: "fixed",
        top: "0",
        left: "0",
        width: "100%",
        height: "100%",
        background: "rgba(0, 0, 0, 0.7)",
        display: "none",
        justifyContent: "center",
        alignItems: "center",
        transition: "opacity 0.3s ease-in-out",
    });

    // Meme Box (White Container)
    Object.assign(memeBox.style, {
        background: "white",
        padding: "20px",
        borderRadius: "12px",
        boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.3)",
        textAlign: "center",
        maxWidth: "350px",
        width: "90%",
        position: "relative",
    });

    // Meme Image (Rounded, Smaller)
    Object.assign(memeImage.style, {
        width: "250px",
        height: "250px",
        borderRadius: "12px",
        boxShadow: "0px 2px 8px rgba(0, 0, 0, 0.2)",
        display: "none",
        marginBottom: "10px",
    });

    // Select Meme Button (Material UI Style)
    Object.assign(selectMemeButton.style, {
        background: "#6200ea",
        color: "white",
        border: "none",
        padding: "10px 16px",
        borderRadius: "8px",
        cursor: "pointer",
        transition: "background 0.3s",
        display: "none",
    });

    selectMemeButton.innerText = "Select Meme";
    selectMemeButton.addEventListener("mouseover", () => {
        selectMemeButton.style.background = "#3700b3";
    });
    selectMemeButton.addEventListener("mouseout", () => {
        selectMemeButton.style.background = "#6200ea";
    });

    // Close Button (X)
    Object.assign(closeMemeButton.style, {
        position: "absolute",
        top: "10px",
        right: "15px",
        fontSize: "20px",
        cursor: "pointer",
        color: "#777",
    });

    closeMemeButton.innerHTML = "&times;";
    closeMemeButton.addEventListener("click", closeMeme);

    // Loader (While Fetching Meme)
    Object.assign(loader.style, {
        fontSize: "18px",
        textAlign: "center",
        padding: "10px",
        display: "none",
    });

    loader.innerText = "Loading Meme...";

    // Append elements
    memeBox.appendChild(closeMemeButton);
    memeBox.appendChild(loader);
    memeBox.appendChild(memeImage);
    memeBox.appendChild(selectMemeButton);
    memeModal.appendChild(memeBox);
    document.body.appendChild(memeModal);

    // Open Meme Modal when "/meme" is typed
    inputField.addEventListener("input", function () {
        if (inputField.value.trim() === "/meme") {
            inputField.value = ""; // Clear input
            memeModal.style.display = "flex"; // Show modal
            memeModal.style.opacity = "0";
            setTimeout(() => {
                memeModal.style.opacity = "1";
            }, 100);
            fetchMeme(); // Fetch meme
        }
    });

    // Fetch a random meme
    function fetchMeme() {
        memeImage.style.display = "none";
        selectMemeButton.style.display = "none";
        loader.style.display = "block"; // Show loader

        fetch("https://api.memegen.link/templates")
            .then(response => response.json())
            .then(templates => {
                const randomTemplate = templates[Math.floor(Math.random() * templates.length)].id;
                const memeURL = `https://api.memegen.link/images/${randomTemplate}/This_is_a_meme/Enjoy_it.png`;

                memeImage.src = memeURL;
                memeImage.style.display = "block";
                memeImage.style.animation = "fadeIn 0.5s ease-in-out";
                selectMemeButton.style.display = "block";
            })
            .catch(error => alert("Error fetching meme: " + error))
            .finally(() => {
                loader.style.display = "none"; // Hide loader
            });
    }

    // Select Meme and insert into input field
    selectMemeButton.addEventListener("click", function () {
        inputField.value = memeImage.src; // Insert meme link
        closeMeme();
    });

    // Close Meme Modal
    function closeMeme() {
        memeModal.style.opacity = "0";
        setTimeout(() => {
            memeModal.style.display = "none";
        }, 200);
    }

    // Close Modal when clicking outside
    window.addEventListener("click", function (event) {
        if (event.target === memeModal) {
            closeMeme();
        }
    });
});


// /DEFINE (WORD)
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");

    inputField.addEventListener("input", function () {
        if (inputField.value.startsWith("/define ")) {
            const word = inputField.value.replace("/define ", "").trim();
            if (word) {
                setTimeout(() => {
                    fetchDefinition(word);
                }, 100); // Small delay for UX
            }
        }
    });

    function fetchDefinition(word) {
        fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${word}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Word not found! ❌");
                }
                return response.json();
            })
            .then(data => {
                if (data && data.length > 0 && data[0].meanings.length > 0) {
                    const meaning = data[0].meanings[0].definitions[0].definition;
                    inputField.value = `📖 "${word}": ${meaning}`;
                } else {
                    inputField.value = `❌ No definition found for "${word}".`;
                }
            })
            .catch(error => {
                inputField.value = `⚠️ ${error.message}`;
            });
    }
});


// /translate <text> <language>
// /translate <text> <language>

document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    let translateTimeout;
    
    inputField.addEventListener("input", function () {
        clearTimeout(translateTimeout); // Clear any previous timeout to avoid unnecessary requests

        const userInput = inputField.value.trim();
        if (userInput.startsWith("/translate ")) {
            translateTimeout = setTimeout(() => {
                const parts = userInput.split(" ");
                if (parts.length >= 3) {
                    const textToTranslate = parts.slice(1, parts.length - 1).join(" ");
                    const targetLanguage = parts[parts.length - 1];

                    showLoadingState(); // Apply Material UI styled loading effect
                    fetchTranslation(textToTranslate, targetLanguage);
                }
            }, 500); // Small delay to ensure user completes typing
        }
    });

    function showLoadingState() {
        inputField.value = ""; // Clear the input field
        inputField.style.backgroundColor = "#f5f5f5"; // Light gray background
        inputField.style.color = "#555"; // Dark gray text
        inputField.style.fontWeight = "bold";
        inputField.style.textAlign = "center";
        inputField.style.padding = "12px";
        inputField.style.borderRadius = "8px";
        inputField.style.transition = "all 0.3s ease-in-out";

        inputField.placeholder = "⏳ Translating..."; // Show loading text in placeholder
    }

    function resetInputStyle(translatedText) {
        inputField.style.backgroundColor = "#fff"; // Reset to white
        inputField.style.color = "#000"; // Reset text color
        inputField.style.textAlign = "left";
        inputField.style.fontWeight = "normal";
        inputField.placeholder = "Type a message...";
        inputField.value = translatedText;
    }

    function fetchTranslation(text, lang) {
        fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=en|${lang}`)
            .then(response => response.json())
            .then(data => {
                if (data.responseData && data.responseData.translatedText) {
                    resetInputStyle(data.responseData.translatedText);
                } else {
                    resetInputStyle("Translation not found.");
                }
            })
            .catch(error => {
                resetInputStyle("Error fetching translation.");
            });
    }
});


// /timer <minutes>
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    const countdownTimer = document.getElementById("countdownTimer");
    const timerMessage = document.getElementById("timerMessage");
    const startStopButton = document.getElementById("startStopTimer");
    const resetButton = document.getElementById("resetTimer");

    let timerInterval;
    let timeLeft;
    let isRunning = false;
    let initialTime;
    let typingTimeout;

    inputField.addEventListener("input", function () {
        clearTimeout(typingTimeout); // Clear previous timeout to allow proper timing

        const userInput = inputField.value.trim();
        if (userInput.startsWith("/timer ")) {
            const parts = userInput.split(" ");
            if (parts.length === 2) {
                const minutes = parseInt(parts[1]);
                if (!isNaN(minutes) && minutes > 0) {
                    // Wait 3 seconds to ensure the user finishes typing
                    typingTimeout = setTimeout(() => {
                        // Show loading effect before the timer starts
                        timerMessage.innerHTML = `<span class="mui-loader">⏳ Preparing timer...</span>`;

                        setTimeout(() => {
                            inputField.value = ""; // Clear input field
                            startCountdown(minutes);
                        }, 1000); // Another 2 seconds delay before starting the timer
                    }, 2000); // 3 seconds delay after user enters time
                }
            }
        }
    });

    function startCountdown(minutes) {
        timeLeft = minutes * 60;
        initialTime = timeLeft;
        updateTimerDisplay(timeLeft);

        // Open Bootstrap Modal
        const timerModal = new bootstrap.Modal(document.getElementById("timerModal"));
        timerModal.show();

        clearInterval(timerInterval); // Reset any existing timer
        startTimer();
    }

    function startTimer() {
        if (!isRunning) {
            isRunning = true;
            timerMessage.innerHTML = `<span class="mui-running">✅ Timer is running...</span>`;
            startStopButton.innerHTML = '<i class="fas fa-pause"></i>'; // Change to Pause Icon

            timerInterval = setInterval(() => {
                timeLeft--;
                updateTimerDisplay(timeLeft);

                if (timeLeft <= 0) {
                    clearInterval(timerInterval);
                    countdownTimer.innerHTML = "00:00";
                    timerMessage.innerHTML = `<span class="mui-complete">🎉 Time's up!</span>`;
                    startStopButton.innerHTML = '<i class="fas fa-play"></i>'; // Reset to Play Icon
                    isRunning = false;
                }
            }, 1000);
        } else {
            clearInterval(timerInterval);
            isRunning = false;
            timerMessage.innerHTML = `<span class="mui-paused">⏸️ Timer Paused.</span>`;
            startStopButton.innerHTML = '<i class="fas fa-play"></i>'; // Change back to Play Icon
        }
    }

    function resetTimer() {
        clearInterval(timerInterval);
        timeLeft = initialTime;
        updateTimerDisplay(timeLeft);
        isRunning = false;
        timerMessage.innerHTML = `<span class="mui-reset">🔄 Timer Reset.</span>`;
        startStopButton.innerHTML = '<i class="fas fa-play"></i>'; // Change back to Play Icon
    }

    function updateTimerDisplay(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        countdownTimer.innerHTML = `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    }

    startStopButton.addEventListener("click", startTimer);
    resetButton.addEventListener("click", resetTimer);
});







// /emoji text
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    let emojiTimeout;

    inputField.addEventListener("input", function () {
        clearTimeout(emojiTimeout); // Clear previous timeout to avoid unnecessary requests

        if (inputField.value.startsWith("/emoji ")) {
            emojiTimeout = setTimeout(() => {
                const textToConvert = inputField.value.replace("/emoji ", "").trim();
                if (textToConvert) {
                    inputField.value = "Fetching emojis... 🔄"; // Show loading effect
                    fetchEmoji(textToConvert);
                }
            }, 500); // Delay before fetching
        }
    });

    function fetchEmoji(text) {
        fetch(`https://api.funtranslations.com/translate/emoji.json?text=${encodeURIComponent(text)}`)
            .then(response => response.json())
            .then(data => {
                if (data && data.contents && data.contents.translated) {
                    inputField.value = decodeHTMLEntities(data.contents.translated); // Convert to real emoji
                } else {
                    inputField.value = "No emojis found. 😢";
                }
            })
            .catch(error => {
                inputField.value = "Error fetching emojis. ❌";
            });
    }

    function decodeHTMLEntities(text) {
        const textarea = document.createElement("textarea");
        textarea.innerHTML = text;
        return textarea.value; // Converts &x1F3E9; to 🏩
    }
});


// /WEATHER <CITY>/

document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    let weatherTimeout;
    let weatherChart;

    inputField.addEventListener("input", function () {
        clearTimeout(weatherTimeout);

        const userInput = inputField.value.trim();
        if (userInput.startsWith("/weather ")) {
            weatherTimeout = setTimeout(() => {
                const parts = userInput.split(" ");
                if (parts.length >= 2) {
                    const city = parts.slice(1).join(" ");
                    inputField.value = ""; // Clear input
                    fetchCityDetails(city);
                }
            }, 700); // Delay for better user input
        }
    });

    function fetchCityDetails(city) {
        // Fetch city details (Latitude, Longitude, Country, Population)
        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city)}`)
            .then(response => response.json())
            .then(locationData => {
                if (locationData.length > 0) {
                    const { lat, lon, display_name } = locationData[0];

                    // Fetch weather data from Open-Meteo
                    fetchWeather(city, lat, lon, display_name);
                } else {
                    showError("City not found.");
                }
            })
            .catch(() => showError("Error fetching city data."));
    }

    function fetchWeather(city, lat, lon, display_name) {
        fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&hourly=temperature_2m&current_weather=true`)
            .then(response => response.json())
            .then(weatherData => {
                if (weatherData.current_weather) {
                    updateWeatherModal(city, weatherData, display_name);
                } else {
                    showError("Weather data not available.");
                }
            })
            .catch(() => showError("Error fetching weather data."));
    }

    function updateWeatherModal(city, weatherData, display_name) {
        const currentWeather = weatherData.current_weather;
        document.getElementById("weatherCity").textContent = city;
        document.getElementById("weatherTemp").innerHTML = `${currentWeather.temperature}°C`;
        document.getElementById("weatherDesc").innerHTML = getWeatherEmoji(currentWeather.weathercode);
        document.getElementById("weatherWind").innerHTML = `💨 Wind Speed: ${currentWeather.windspeed} km/h`;
        document.getElementById("weatherTime").innerHTML = `🕒 Last Updated: ${new Date().toLocaleTimeString()}`;

        // Set city details
        document.getElementById("cityDetails").innerHTML = `
            <p><strong>📍 Location:</strong> ${display_name}</p>
            <p><strong>🌍 Latitude:</strong> ${weatherData.latitude}</p>
            <p><strong>🌍 Longitude:</strong> ${weatherData.longitude}</p>
        `;

        // Display the modal
        const weatherModal = new bootstrap.Modal(document.getElementById("weatherModal"));
        weatherModal.show();

        // Render the temperature chart
        renderWeatherChart(weatherData.hourly.temperature_2m);
    }

    function renderWeatherChart(temperatureData) {
        const ctx = document.getElementById("weatherChart").getContext("2d");
    
        if (weatherChart) {
            weatherChart.destroy(); // Destroy previous chart if exists
        }
    
        weatherChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: Array.from({ length: temperatureData.length }, (_, i) => `${i}:00`), // Hour labels
                datasets: [{
                    label: "Temperature (°C)",
                    data: temperatureData,
                    borderColor: "#ff4757",
                    backgroundColor: "rgba(255, 71, 87, 0.2)",
                    borderWidth: 2,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: { color: "#333", font: { size: 14 } }
                    },
                    x: {
                        ticks: { color: "#333", font: { size: 14 } }
                    }
                }
            }
        });
    }
    

    function showError(message) {
        document.getElementById("weatherCity").textContent = "Error";
        document.getElementById("weatherTemp").innerHTML = "❌";
        document.getElementById("weatherDesc").innerHTML = message;
        document.getElementById("weatherWind").innerHTML = "";
        document.getElementById("weatherTime").innerHTML = "";
        document.getElementById("cityDetails").innerHTML = "";

        const weatherModal = new bootstrap.Modal(document.getElementById("weatherModal"));
        weatherModal.show();
    }

    function getWeatherEmoji(code) {
        const weatherIcons = {
            0: "☀️ Clear Sky",
            1: "🌤️ Mainly Clear",
            2: "⛅ Partly Cloudy",
            3: "☁️ Overcast",
            45: "🌫️ Fog",
            48: "🌫️ Depositing Rime Fog",
            51: "🌦️ Drizzle",
            61: "🌧️ Rain",
            71: "❄️ Snow",
            95: "⛈️ Thunderstorm"
        };
        return weatherIcons[code] || "❓ Unknown Weather";
    }
});



// /docs [tech]
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");

    let timer;  // Timer to delay request

    inputField.addEventListener("input", function () {
        clearTimeout(timer); // Reset timer on new input

        const userInput = inputField.value.trim();
        if (userInput.startsWith("/docs ")) {
            timer = setTimeout(() => {
                const parts = userInput.split(" ");
                if (parts.length === 2) {
                    const tech = parts[1].toLowerCase();
                    fetchDocs(tech);
                }
            }, 3000); // 3 seconds delay for user to type
        }
    });

    function fetchDocs(tech) {
        inputField.value = "Fetching docs..."; // Show loading message

        fetch(`/dm/fetch-docs/${tech}/`)
            .then(response => response.json())
            .then(data => {
                if (data.docs) {
                    displayDocs(data.docs, tech);
                } else {
                    inputField.value = "Documentation not found.";
                }
            })
            .catch(() => {
                inputField.value = "Error fetching documentation.";
            });
    }

    function displayDocs(docs, tech) {
        let modalBody = document.getElementById("docsModalBody");
        modalBody.innerHTML = `<h4 class="doc-title">${tech.toUpperCase()} Documentation</h4>`;

        docs.forEach(doc => {
            const docItem = document.createElement("div");
            docItem.classList.add("doc-item");

            docItem.innerHTML = `
                <a href="${doc}" target="_blank" class="doc-link">${doc}</a>
                <button class="doc-copy-btn">➕</button>
            `;

            // Append to input when clicked
            docItem.querySelector(".doc-copy-btn").addEventListener("click", function () {
                inputField.value += ` ${doc}`;
                inputField.focus();
            });

            modalBody.appendChild(docItem);
        });

        let docsModal = new bootstrap.Modal(document.getElementById("docsModal"));
        docsModal.show();
    }
});



// /roast (FETCH ROASTS INSTANTLY)
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");

    inputField.addEventListener("input", function () {
        if (inputField.value.trim() === "/roast") {
            inputField.value = ""; // Clear input
            fetchRoast(); // Fetch a roast
        }
    });

    function fetchRoast() {
        fetch("/dm/fetch-roast/")
            .then(response => response.json())
            .then(data => {
                if (data.roast) {
                    displayRoast(data.roast);
                } else {
                    displayRoast("You're so unroastable, even fire gives up on you. 🔥😂");
                }
            })
            .catch(() => {
                displayRoast("Oops! The roast master is sleeping. Try again later.");
            });
    }

    function displayRoast(roast) {
        let modalBody = document.getElementById("roastModalBody");
        modalBody.innerHTML = `
            <div class="roast-container">
                <p class="roast-text">${roast}</p>
                <div class="roast-actions">
                    <span class="send-roast" data-roast="${roast}">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 2 11 13"></path>
                            <path d="M22 2 15 22 11 13 2 9 22 2z"></path>
                        </svg>
                    </span>
                    <span class="get-another-roast">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 2v4"></path>
                            <path d="M12 18v4"></path>
                            <path d="M4.93 4.93l2.83 2.83"></path>
                            <path d="M16.24 16.24l2.83 2.83"></path>
                            <path d="M2 12h4"></path>
                            <path d="M18 12h4"></path>
                            <path d="M4.93 19.07l2.83-2.83"></path>
                            <path d="M16.24 7.76l2.83-2.83"></path>
                        </svg>
                    </span>
                </div>
            </div>
        `;

        let roastModal = new bootstrap.Modal(document.getElementById("roastModal"));
        roastModal.show();

        // Attach event listeners for send and get new roast
        document.querySelector(".send-roast").addEventListener("click", function () {
            inputField.value = this.getAttribute("data-roast");
        });

        document.querySelector(".get-another-roast").addEventListener("click", function () {
            fetchRoast();
        });
    }
});


// /ping (current network status)
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    let pingTriggered = false; // Prevent duplicate requests

    inputField.addEventListener("input", function () {
        const userInput = inputField.value.trim();

        if (userInput.startsWith("/ping") && !pingTriggered) {
            pingTriggered = true; // Mark as triggered to prevent duplicate requests
            fetchPingStats();
        }
    });

    function fetchPingStats() {
        inputField.value = "Fetching ping stats..."; // Show loading message

        fetch("/dm/fetch-ping-stats/")
            .then(response => response.json())
            .then(data => {
                if (data) {
                    displayPingModal(data);
                } else {
                    inputField.value = "No data available.";
                }
                pingTriggered = false; // Reset trigger after request completes
            })
            .catch(() => {
                inputField.value = "Error fetching ping stats.";
                pingTriggered = false; // Reset on error
            });
    }

    function displayPingModal(data) {
        let modalBody = document.getElementById("pingModalBody");
        modalBody.innerHTML = `
            <h4 class="modal-title">📊 System & Network Statistics</h4>
            <p class="system-uptime">System Uptime: ${data.system_uptime}</p>
            <div class="chart-grid">
                <div class="chart-container"><canvas id="pingChart"></canvas></div>
                <div class="chart-container"><canvas id="speedChart"></canvas></div>
                <div class="chart-container"><canvas id="apiLatencyChart"></canvas></div>
                <div class="chart-container"><canvas id="cpuUsageChart"></canvas></div>
                <div class="chart-container"><canvas id="memoryUsageChart"></canvas></div>
                <div class="chart-container"><canvas id="diskUsageChart"></canvas></div>
                <div class="chart-container"><canvas id="activeProcessesChart"></canvas></div>
                <div class="chart-container"><canvas id="networkUsageChart"></canvas></div>
            </div>
        `;

        let pingModal = new bootstrap.Modal(document.getElementById("pingModal"));
        pingModal.show();

        setTimeout(() => {
            renderPingChart(data);
            renderSpeedChart(data);
            renderApiLatencyChart(data);
            renderCPUUsageChart(data);
            renderMemoryUsageChart(data);
            renderDiskUsageChart(data);
            renderActiveProcessesChart(data);
            renderNetworkUsageChart(data);
        }, 500);
    }

    function renderPingChart(data) {
        new Chart(document.getElementById("pingChart").getContext("2d"), {
            type: "line",
            data: {
                labels: ["Min", "Avg", "Max"],
                datasets: [{
                    label: "Ping Times (ms)",
                    data: [data.server_response_times.min, data.server_response_times.avg, data.server_response_times.max],
                    borderColor: "#FF6384",
                    backgroundColor: "rgba(255,99,132,0.5)",
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            }
        });
    }

    function renderSpeedChart(data) {
        new Chart(document.getElementById("speedChart").getContext("2d"), {
            type: "bar",
            data: {
                labels: ["Download", "Upload"],
                datasets: [{
                    label: "Speed (Mbps)",
                    data: [data.network_speed.download_speed, data.network_speed.upload_speed],
                    backgroundColor: ["#36A2EB", "#4CAF50"],
                    borderRadius: 10
                }]
            }
        });
    }

    function renderApiLatencyChart(data) {
        new Chart(document.getElementById("apiLatencyChart").getContext("2d"), {
            type: "line",
            data: {
                labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                datasets: [{
                    label: "API Latency (ms)",
                    data: data.api_latency,
                    borderColor: "#FFA500",
                    backgroundColor: "rgba(255,165,0,0.5)",
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            }
        });
    }

    function renderCPUUsageChart(data) {
        new Chart(document.getElementById("cpuUsageChart").getContext("2d"), {
            type: "line",
            data: {
                labels: ["CPU Usage"],
                datasets: [{
                    label: "CPU Usage (%)",
                    data: [data.cpu_usage],
                    borderColor: "#FF5733",
                    backgroundColor: "rgba(255,87,51,0.5)",
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            }
        });
    }

    function renderMemoryUsageChart(data) {
        new Chart(document.getElementById("memoryUsageChart").getContext("2d"), {
            type: "doughnut",
            data: {
                labels: ["Used", "Free"],
                datasets: [{
                    data: [data.memory_usage, 100 - data.memory_usage],
                    backgroundColor: ["#8E44AD", "#D5DBDB"]
                }]
            }
        });
    }

    function renderDiskUsageChart(data) {
        new Chart(document.getElementById("diskUsageChart").getContext("2d"), {
            type: "doughnut",
            data: {
                labels: ["Used", "Free"],
                datasets: [{
                    data: [data.disk_usage, 100 - data.disk_usage],
                    backgroundColor: ["#2ECC71", "#D5DBDB"]
                }]
            }
        });
    }

    function renderActiveProcessesChart(data) {
        new Chart(document.getElementById("activeProcessesChart").getContext("2d"), {
            type: "bar",
            data: {
                labels: ["Active Processes"],
                datasets: [{
                    label: "Processes Count",
                    data: [data.active_processes],
                    backgroundColor: "#3498DB",
                    borderRadius: 10
                }]
            }
        });
    }

    function renderNetworkUsageChart(data) {
        new Chart(document.getElementById("networkUsageChart").getContext("2d"), {
            type: "bar",
            data: {
                labels: ["Sent", "Received"],
                datasets: [{
                    label: "Network Usage (MB)",
                    data: [data.network_usage.sent, data.network_usage.received],
                    backgroundColor: ["#E74C3C", "#F1C40F"],
                    borderRadius: 10
                }]
            }
        });
    }
});
 


// /calc <expression>

document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    
    inputField.addEventListener("input", function () {
        const userInput = inputField.value.trim();

        // Check if the input starts with /calc and has an expression inside <>
        const calcRegex = /^\/calc\s*<(.+)>$/;
        const match = userInput.match(calcRegex);

        if (match) {
            const expression = match[1].trim(); // Extract the math expression

            try {
                // Evaluate the expression safely
                const result = new Function(`return (${expression})`)(); 
                
                if (!isNaN(result)) {
                    inputField.value = `/calc <${expression}> = ${result}`; // Append result
                } else {
                    inputField.value = "Invalid calculation!";
                }
            } catch (error) {
                inputField.value = "Error in expression!";
            }
        }
    });
});


// /wiki <query>
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    let wikiTriggered = false;
    let typingTimer; // Timer for delay

    const loaderHTML = `
        <div class="wiki-loader-container">
            <div class="wiki-loader"></div>
            <span class="wiki-loader-text">Fetching Wikipedia...</span>
        </div>
    `;

    inputField.addEventListener("input", function () {
        clearTimeout(typingTimer); // Reset timer on each keystroke
        const userInput = inputField.value.trim();

        if (userInput.startsWith("/wiki")) {
            typingTimer = setTimeout(() => {
                if (!wikiTriggered) {
                    wikiTriggered = true;
                    console.log("Wiki command detected!"); // ✅ Debugging

                    const query = userInput.replace("/wiki", "").trim();
                    if (query) {
                        console.log(`Fetching Wikipedia for: ${query}`); // ✅ Debugging
                        fetchWikiData(query);
                    } else {
                        wikiTriggered = false; // Reset trigger if no query
                    }
                }
            }, 3000); // 3 seconds delay
        }
    });

    function fetchWikiData(query) {
        inputField.value = ""; // Clear input
        inputField.insertAdjacentHTML("afterend", loaderHTML); // Show Material UI Spinner

        fetch(`/dm/fetch-wiki/?query=${encodeURIComponent(query)}`)
            .then(response => {
                console.log("Fetch request sent!"); // ✅ Debugging
                return response.json();
            })
            .then(data => {
                console.log("Response received:", data); // ✅ Debugging
                document.querySelector(".wiki-loader-container")?.remove(); // Remove Spinner

                if (data.extract) {
                    displayWikiModal(data);
                } else {
                    inputField.value = "No Wikipedia data found.";
                }
                wikiTriggered = false;
            })
            .catch(error => {
                console.error("Fetch error:", error); // ✅ Debugging
                document.querySelector(".wiki-loader-container")?.remove(); // Remove Spinner
                inputField.value = "Error fetching Wikipedia details.";
                wikiTriggered = false;
            });
    }

    function displayWikiModal(data) {
        let modalBody = document.getElementById("wikiModalBody");
        modalBody.innerHTML = `
            <div class="wiki-card">
                <h4 class="wiki-title">${data.title}</h4>
                <p class="wiki-text">${data.extract}</p>
                ${data.thumbnail ? `<img src="${data.thumbnail.source}" class="wiki-image" alt="${data.title}">` : ""}
                <p><a href="${data.content_urls.desktop.page}" target="_blank" class="wiki-link">Read more on Wikipedia</a></p>
                <button class="btn btn-primary select-content-btn">📌 Select Content</button>
            </div>
        `;

        let wikiModal = new bootstrap.Modal(document.getElementById("wikiModal"));
        wikiModal.show();

        // Attach event listener to "Select Content" button
        document.querySelector(".select-content-btn").addEventListener("click", function () {
            inputField.value = `/wiki ${data.extract.substring(0, 100)}...`; // Append first 100 chars
            wikiModal.hide();
        });
    }
});


// /git <username>

// /git <username>
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    let gitTriggered = false;
    let typingTimer;

    inputField.addEventListener("input", function () {
        clearTimeout(typingTimer);
        const userInput = inputField.value.trim();

        if (userInput.startsWith("/git")) {
            typingTimer = setTimeout(() => {
                if (!gitTriggered) {
                    gitTriggered = true;
                    const username = userInput.replace("/git", "").trim();
                    if (username) {
                        fetchGitHubData(username);
                    } else {
                        gitTriggered = false;
                    }
                }
            }, 3000); // 3 seconds delay
        }
    });

    function fetchGitHubData(username) {
        inputField.value = "";
        inputField.insertAdjacentHTML("afterend", `<div class="git-loader">Fetching GitHub data...</div>`);

        fetch(`/dm/fetch-github/?username=${encodeURIComponent(username)}`)
            .then(response => response.json())
            .then(data => {
                document.querySelector(".git-loader").remove();

                if (data.user) {
                    displayGitHubModal(data.user);
                } else {
                    inputField.value = "GitHub user not found.";
                }
                gitTriggered = false;
            })
            .catch(error => {
                console.error("Fetch error:", error);
                inputField.value = "Error fetching GitHub details.";
                gitTriggered = false;
            });
    }

    function displayGitHubModal(user) {
        let modalBody = document.getElementById("gitModalBody");
        modalBody.innerHTML = `
            <div class="git-dashboard">
                <div class="git-header">
                    <img src="${user.avatarUrl}" class="git-avatar">
                    <div class="git-user-info">
                        <h2>${user.name || user.login}</h2>
                        <p>${user.bio || "No bio available"}</p>
                        <p><i class="fas fa-map-marker-alt"></i> ${user.location || "Unknown"}</p>
                        <p><a href="${user.websiteUrl}" target="_blank">${user.websiteUrl || "No Website"}</a></p>
                    </div>
                </div>
                <div class="git-stats">
                    <div><strong>Followers:</strong> ${user.followers.totalCount}</div>
                    <div><strong>Following:</strong> ${user.following.totalCount}</div>
                </div>
                <h3>Top Repositories</h3>
                <div class="git-repos">
                    ${user.repositories.nodes.map(repo => `
                        <div class="git-repo">
                            <a href="${repo.url}" target="_blank"><strong>${repo.name}</strong></a>
                            <p>${repo.description || "No description"}</p>
                            <span>⭐ ${repo.stargazers.totalCount}</span>
                        </div>
                    `).join("")}
                </div>
            </div>
        `;

        let gitModal = new bootstrap.Modal(document.getElementById("gitModal"));
        gitModal.show();
    }
});


// /uuid (Generate UUID for development purposes)

document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");

    inputField.addEventListener("input", function () {
        const userInput = inputField.value.trim();

        if (userInput === "/uuid") {
            const uuid = generateUUID();
            inputField.value = uuid;
            inputField.setSelectionRange(uuid.length, uuid.length); // Move cursor to the end
        }
    });

    function generateUUID() {
        return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (char) {
            const rand = (Math.random() * 16) | 0;
            const value = char === "x" ? rand : (rand & 0x3) | 0x8;
            return value.toString(16);
        });
    }
});


// /generate <topic> (Generates blog on the topic)
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    let typingTimer;
    let generateTriggered = false;

    inputField.addEventListener("input", function () {
        clearTimeout(typingTimer);
        const userInput = inputField.value.trim();

        if (userInput.startsWith("/generate")) {
            typingTimer = setTimeout(() => {
                if (!generateTriggered) {
                    generateTriggered = true;
                    let topic = userInput.replace("/generate", "").trim();
                    if (topic) {
                        fetchGeneratedContent(topic);
                    } else {
                        generateTriggered = false;
                    }
                }
            }, 4000); // 4-second delay
        }
    });

    function fetchGeneratedContent(topic) {
        inputField.value = "";
        inputField.insertAdjacentHTML("afterend", `<div class="gen-loader">Generating content...</div>`);

        fetch(`/dm/generate-content/?topic=${encodeURIComponent(topic)}`)
            .then(response => response.json())
            .then(data => {
                document.querySelector(".gen-loader").remove();
                
                if (data.content) {
                    displayGeneratedModal(data.content);
                } else {
                    displayGeneratedModal("Error generating content.");
                }
                generateTriggered = false;
            })
            .catch(error => {
                console.error("Fetch error:", error);
                displayGeneratedModal("Error fetching content.");
                generateTriggered = false;
            });
    }

    function displayGeneratedModal(content) {
        let modalBody = document.getElementById("generateModalBody");
        modalBody.innerHTML = `<p>${content}</p>`;

        let generateModal = new bootstrap.Modal(document.getElementById("generateModal"));
        generateModal.show();
    }
});


// /code <topic> <language>
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    let codeTriggered = false;
    let typingTimer;

    inputField.addEventListener("input", function () {
        clearTimeout(typingTimer);
        const userInput = inputField.value.trim();

        if (userInput.startsWith("/code")) {
            typingTimer = setTimeout(() => {
                if (!codeTriggered) {
                    codeTriggered = true;
                    const parts = userInput.split(" ").slice(1);
                    const topic = parts.slice(0, -1).join(" ");
                    const language = parts.slice(-1)[0];

                    if (topic && language) {
                        fetchCodeSnippet(topic, language);
                    } else {
                        inputField.value = "Invalid format. Use: /code <topic> <language>";
                        codeTriggered = false;
                    }
                }
            }, 4000);
        }
    });

    function fetchCodeSnippet(topic, language) {
        inputField.value = "";

        // Insert Material UI-style spinner
        const spinnerHTML = `
            <div class="gen-loader">
                <div class="spinner"></div>
                <span>Generating Code...</span>
            </div>
        `;
        inputField.insertAdjacentHTML("afterend", spinnerHTML);

        fetch(`/dm/generate-code/?topic=${encodeURIComponent(topic)}&language=${encodeURIComponent(language)}`)
            .then(response => response.json())
            .then(data => {
                document.querySelector(".gen-loader").remove();

                if (data.code) {
                    displayProgrammingModal(data.code, data.language);
                } else {
                    inputField.value = data.error || "Error generating code.";
                }
                codeTriggered = false;
            })
            .catch(error => {
                console.error("Fetch error:", error);
                document.querySelector(".gen-loader").remove();
                inputField.value = "Error fetching code.";
                codeTriggered = false;
            });
    }

    function displayProgrammingModal(code, language) {
        let modalBody = document.getElementById("ProgrammingModalBody");
        modalBody.innerHTML = `
            <pre class="code-container"><code class="language-${language}">${code}</code></pre>
            <button class="btn btn-primary copy-btn" onclick="copyCode()">Copy Code</button>
        `;

        let programmingModal = new bootstrap.Modal(document.getElementById("ProgrammingModal"));
        programmingModal.show();

        Prism.highlightAll(); // Apply syntax highlighting
    }

    function copyCode() {
        const codeElement = document.querySelector("#ProgrammingModalBody pre code");
        const textArea = document.createElement("textarea");
        textArea.value = codeElement.textContent;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);

        alert("Code copied to clipboard!");
    }
});


// /Embed <website_url>8

document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    const embedSelectionModal = new bootstrap.Modal(document.getElementById("EmbedSelectionModal"));
    const embedModal = new bootstrap.Modal(document.getElementById("EmbedModal"));
    const embedContainer = document.getElementById("EmbedContainer");
    const manualUrlInput = document.getElementById("manualUrlInput");
    const embedChoices = document.querySelectorAll(".embed-choice");

    // Detect /embed command
    inputField.addEventListener("input", function () {
        if (inputField.value.trim() === "/embed") {
            inputField.value = "";
            embedSelectionModal.show();
        }
    });

    // Predefined choices
    embedChoices.forEach(choice => {
        choice.addEventListener("click", function () {
            const embedUrl = this.getAttribute("data-url");
            openEmbedModal(embedUrl);
        });
    });

    // Manual URL submission
    document.getElementById("embedManualBtn").addEventListener("click", function () {
        const userUrl = manualUrlInput.value.trim();
        if (userUrl) {
            openEmbedModal(userUrl);
        }
    });

    // Function to open the embed modal with an iframe
    function openEmbedModal(embedUrl) {
        embedContainer.innerHTML = `<iframe src="${embedUrl}" class="embed-iframe" allowfullscreen></iframe>`;
        embedSelectionModal.hide();
        setTimeout(() => {
            embedModal.show();
        }, 500);
    }
});





// /ai queries
// /ai queries with Tailwind styling (Modal Opening Fixed)
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");
    const aiChatModalEl = document.getElementById("aiChatModal");
    const aiChatModal = new bootstrap.Modal(aiChatModalEl, { backdrop: 'static', keyboard: false }); // Prevent auto-opening
    const aiChatInput = document.getElementById("aiChatInput");
    const aiChatSend = document.getElementById("aiChatSend");
    const aiChatMessages = document.getElementById("aiChatMessages");
    const predefinedQueriesContainer = document.getElementById("predefinedQueries");

    // Ensure modal is hidden on load
    aiChatModalEl.classList.remove("show");
    aiChatModalEl.style.display = "none";

    // Detect /ai command and force open modal
    inputField.addEventListener("input", function () {
        if (inputField.value.trim() === "/ai") {
            inputField.value = "";
            aiChatModal.show();  // Open modal only when command is typed
            aiChatInput.focus();
        }
    });

    // Predefined queries
    const queries = [
        "What is my next meeting?",
        "How many todos do I have?",
        "Summarize my conversations",
        "List my pending tasks",
        "Tell me a random fact!",
        "Tell me my events I created?",
    ];

    // Generate query buttons with Tailwind styling
    predefinedQueriesContainer.innerHTML = "";
    queries.forEach(query => {
        let queryBtn = document.createElement("button");
        queryBtn.textContent = query;
        queryBtn.classList.add(
            "px-4", "py-2", "rounded-lg", "shadow-md", "text-white",
            "font-medium", "transition-all", "duration-300",
            "bg-gradient-to-r", "from-blue-500", "to-purple-500",
            "hover:from-purple-500", "hover:to-blue-500", "focus:ring-4", "focus:ring-purple-300"
        );
        queryBtn.addEventListener("click", function () {
            sendMessageToAI(query);
        });
        predefinedQueriesContainer.appendChild(queryBtn);
    });

    // Send message on button click
    aiChatSend.addEventListener("click", function () {
        let userMessage = aiChatInput.value.trim();
        if (!userMessage) return;
        sendMessageToAI(userMessage);
    });

    // Function to send message to AI
    function sendMessageToAI(userMessage) {
        aiChatMessages.innerHTML += `<div class="user-message p-2 bg-blue-500 text-white rounded-md mb-2"><b>You:</b> ${userMessage}</div>`;
        aiChatInput.value = "";

        // Typing animation
        let typingDots = document.createElement("div");
        typingDots.classList.add("ai-message", "typing-animation", "flex", "items-center", "gap-1", "text-gray-500", "font-semibold");
        typingDots.innerHTML = `<b>AI:</b> <span class="dot-animation inline-block w-2 h-2 bg-gray-500 rounded-full animate-bounce"></span>
                                 <span class="dot-animation inline-block w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></span>
                                 <span class="dot-animation inline-block w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-300"></span>`;
        aiChatMessages.appendChild(typingDots);
        aiChatMessages.scrollTop = aiChatMessages.scrollHeight;

        const orgId = window.djangoData.orgId;
        const conversationId = window.djangoData.conversationId;
        const otherUserId = window.djangoData.otherUserId;

        // Send AJAX request to AI backend
        fetch(`/dm/ai_chat_view/${orgId}/${conversationId}/${otherUserId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ message: userMessage }),
        })
            .then(response => response.json())
            .then(data => {
                typingDots.remove();
                aiChatMessages.innerHTML += `<div class="ai-message p-2 bg-gray-200 text-gray-900 rounded-md mb-2"><b>AI:</b> ${data.response}</div>`;
                aiChatMessages.scrollTop = aiChatMessages.scrollHeight;
            })
            .catch(error => {
                console.error("Error:", error);
                typingDots.remove();
                aiChatMessages.innerHTML += `<div class="ai-message error p-2 bg-red-500 text-white rounded-md mb-2"><b>AI:</b> ❌ Error fetching response.</div>`;
            });
    }

    // Function to get CSRF token
    function getCSRFToken() {
        return document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
    }
});



// /shrug
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");

    inputField.addEventListener("input", function (event) {
        const value = inputField.value.trim();

        if (value === "/shrug") {
            inputField.value = "¯\\_(ツ)_/¯ "; // Append shrug emoji
            inputField.setSelectionRange(inputField.value.length, inputField.value.length); // Move cursor to end
        }
    });
});


// Multiple commands
document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("chat-message-input");

    // Command-to-text mapping
    const commandReplacements = {
        "/tableflip": "(╯°□°）╯︵ ┻━┻",
        "/unflip": "┬─┬ ノ( ゜-゜ノ)",
        "/lenny": "( ͡° ͜ʖ ͡°)",
        "/wave": "👋",
        "/happy": "😄",
        "/sad": "😢",
        "/love": "❤️",
        "/shrug": "¯\\_(ツ)_/¯",
        "/yawn": "😴",
        "/excited": "🤩",
        "/angry": "😡",
        "/cry": "😭",
        "/wow": "😲",
        "/facepalm": "🤦",
        "/dance": "💃🕺",
        "/wink": "😉",
        "/cheers": "🥂",
        "/clap": "👏",
        "/thumbsup": "👍",
        "/thumbsdown": "👎",
        "/fire": "🔥",
        "/cool": "😎",
        "/party": "🎉",
        "/sleepy": "🥱",
        "/hug": "🤗",
        "/kiss": "😘",
        "/heart": "💖",
        "/mindblown": "🤯",
        "/star": "⭐",
        "/poop": "💩",
        "/boom": "💥",
        "/ghost": "👻",
        "/robot": "🤖",
        "/skull": "💀",
        "/alien": "👽",
        "/money": "🤑",
        "/coffee": "☕",
        "/tea": "🍵",
        "/pizza": "🍕",
        "/burger": "🍔",
        "/beer": "🍺",
        "/cake": "🎂",
        "/cookie": "🍪",
        "/gift": "🎁"
    };

    // Detect input change
    inputField.addEventListener("input", function () {
        const words = inputField.value.trim().split(/\s+/);
        const lastWord = words[words.length - 1];

        if (commandReplacements[lastWord]) {
            // Replace command with emoji/text
            words[words.length - 1] = commandReplacements[lastWord];
            inputField.value = words.join(" ") + " ";
        }
    });
});




// /emoji <context>
document.getElementById("chat-message-input").addEventListener("input", function () {
    let inputValue = this.value.trim();

    if (inputValue.startsWith("/emoji ")) {
        let searchQuery = inputValue.replace("/emoji ", "").trim();
        if (searchQuery.length > 0) {
            fetchEmojis(searchQuery);
        }
    }
});

function fetchEmojis(query) {
    let apiKey = "ccc1720ab12d0a7db1b42eefc68ae9f9223135f1"; // Replace with your actual API key
    let url = `https://emoji-api.com/emojis?search=${query}&access_key=${apiKey}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log("API Response:", data); // Log to debug response

            if (!Array.isArray(data)) {
                console.error("Emoji API returned unexpected data:", data);
                return;
            }

            let emojis = data.map(emoji => emoji.character).slice(0, 10); // Extract first 10 emojis
            showEmojiModal(emojis);
        })
        .catch(error => console.error("Emoji fetch failed:", error));
}

function showEmojiModal(emojis) {
    let modal = document.getElementById("emoji-modal");
    let emojiContainer = document.getElementById("emoji-list");

    // Clear previous emojis
    emojiContainer.innerHTML = "";

    // Add new emojis
    emojis.forEach(emoji => {
        let btn = document.createElement("button");
        btn.innerHTML = emoji;
        btn.classList.add("emoji-btn", "text-xl", "p-2", "hover:bg-gray-200", "rounded");
        btn.onclick = () => appendEmoji(emoji);
        emojiContainer.appendChild(btn);
    });

    // Show modal
    modal.classList.remove("hidden");
    modal.classList.add("flex");
}

function appendEmoji(emoji) {
    let input = document.getElementById("chat-message-input");
    input.value += " " + emoji;
    closeEmojiModal();
}

function closeEmojiModal() {
    let modal = document.getElementById("emoji-modal");
    modal.classList.add("hidden");
}

// Close modal when clicking outside
window.onclick = function (event) {
    let modal = document.getElementById("emoji-modal");
    if (event.target === modal) {
        closeEmojiModal();
    }
};




// /remind [what] [when]

document.getElementById("chat-message-input").addEventListener("input", function (e) {
    let inputValue = this.value.trim();
    
    if (inputValue.startsWith("/remind ")) {
        let args = inputValue.replace("/remind ", "").trim().split(" ");

        if (args.length < 2) {
            console.warn("Incomplete reminder command");
            return;
        }

        let what = args.slice(0, args.length - 1).join(" "); // Reminder text
        let when = args[args.length - 1]; // Reminder time (last argument)

        let remindAt = parseReminderTime(when); // Convert to proper datetime format

        if (!remindAt) {
            console.warn("Invalid time format, reminder not set");
            return;
        }

        let orgId = window.djangoData?.orgId; // Injected from Django template
        let conversationId = window.djangoData?.conversationId || null; // Can be null

        if (!orgId) {
            console.error("Organization ID is missing");
            return;
        }

        saveReminder(orgId, conversationId, what, remindAt);
        this.value = ""; // Clear input after sending
    }
});

function parseReminderTime(timeStr) {
    try {
        let now = new Date();
        let dateTime;

        if (timeStr.includes(":")) {
            let [hours, minutes] = timeStr.split(":").map(Number);
            dateTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hours, minutes);
        } else if (timeStr.toLowerCase() === "tomorrow") {
            dateTime = new Date(now);
            dateTime.setDate(now.getDate() + 1);
            dateTime.setHours(9, 0, 0); // Default to 9 AM
        } else if (timeStr.toLowerCase() === "nextweek") {
            dateTime = new Date(now);
            dateTime.setDate(now.getDate() + 7);
            dateTime.setHours(9, 0, 0);
        } else {
            console.error("Invalid reminder time input:", timeStr);
            return null;
        }

        return dateTime.toISOString().slice(0, 19).replace("T", " "); // Format: YYYY-MM-DD HH:MM:SS
    } catch (error) {
        console.error("Time parsing error:", error);
        return null;
    }
}

function saveReminder(orgId, conversationId, text, remindAt) {
    let url = `/reminder/save/${orgId}/`;
    if (conversationId) {
        url = `/dm/reminder/save/${orgId}/${conversationId}/`;
    }

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({ text: text, remind_at: remindAt })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("✅ Reminder saved successfully!");
            showSuccessMessage("Reminder set!");
        } else {
            console.error("❌ Error saving reminder:", data.error);
            showErrorMessage("Failed to set reminder!");
        }
    })
    .catch(error => console.error("⚠️ Request failed:", error));
}

// Function to get CSRF token (Required for Django POST requests)
function getCSRFToken() {
    let csrfToken = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
    return csrfToken ? csrfToken.split("=")[1] : "";
}

// Success message display (Replace with modal/toast if needed)
function showSuccessMessage(msg) {
    alert(msg);
}

// Error message display (Replace with modal/toast if needed)
function showErrorMessage(msg) {
    alert(msg);
}


// /browse [URL] - browse a website in chromebrowser
let browseTimeout;

document.getElementById("chat-message-input").addEventListener("input", function (e) {
    let inputValue = this.value.trim();

    if (inputValue.startsWith("/browse")) {
        clearTimeout(browseTimeout);

        browseTimeout = setTimeout(() => {
            let query = inputValue.replace("/browse", "").trim();
            this.value = ""; // Clear input field

            let url;
            if (!query) {
                url = "https://www.google.com"; // Default to Google
            } else if (query.includes(".")) {
                url = query.startsWith("http") ? query : `https://${query}`; // If it's a website URL
            } else {
                url = `https://www.google.com/search?q=${encodeURIComponent(query)}`; // If it's a search
            }

            openMiniBrowser(url);
        }, 3000); // Wait 3 seconds before launching
    }
});

function openMiniBrowser(url) {
    document.getElementById("browserFrame").src = url;
    let modal = new bootstrap.Modal(document.getElementById("browserModal"));
    modal.show();
}

// Function to update the embedded browser URL
function updateBrowserURL() {
    let inputURL = document.getElementById("browserURL").value.trim();
    let finalURL = inputURL.includes(".") ? `https://${inputURL}` : `https://www.google.com/search?q=${encodeURIComponent(inputURL)}`;
    document.getElementById("browserFrame").src = finalURL;
}


// /screenshot - captures the entire screen
document.addEventListener("DOMContentLoaded", function () {
    let screenshotStream = null;

    // Detects /screenshot command and starts screen capture
    document.getElementById("chat-message-input").addEventListener("input", function (e) {
        let inputValue = this.value.trim();

        if (inputValue === "/screenshot") {
            startScreenCapture();
            this.value = "";  // Clear input after command
        }
    });

    async function startScreenCapture() {
        try {
            screenshotStream = await navigator.mediaDevices.getDisplayMedia({ video: true });

            const track = screenshotStream.getVideoTracks()[0];
            const imageCapture = new ImageCapture(track);

            const bitmap = await imageCapture.grabFrame();
            track.stop(); // Stop capturing after screenshot

            let canvas = document.createElement("canvas");
            canvas.width = bitmap.width;
            canvas.height = bitmap.height;
            let ctx = canvas.getContext("2d");
            ctx.drawImage(bitmap, 0, 0);

            let screenshotData = canvas.toDataURL("image/png"); // Convert to Base64

            // Show preview in modal
            let screenshotPreview = document.getElementById("screenshot-preview");
            screenshotPreview.src = screenshotData;
            screenshotPreview.style.display = "block";

            // Open the modal
            let screenshotModal = new bootstrap.Modal(document.getElementById("screenshot-modal"));
            screenshotModal.show();

        } catch (error) {
            console.error("Screen capture failed:", error);
        }
    }

    // Sends the screenshot in the chat container
    document.getElementById("send-screenshot").addEventListener("click", function () {
        let chatContainer = document.getElementById("chat-container");
        let screenshotPreview = document.getElementById("screenshot-preview");

        if (!screenshotPreview.src) {
            console.error("No screenshot available!");
            return;
        }

        let messageDiv = document.createElement("div");
        messageDiv.classList.add("chat-message", "screenshot-message"); 

        let img = document.createElement("img");
        img.src = screenshotPreview.src;
        img.classList.add("sent-screenshot");

        messageDiv.appendChild(img);
        chatContainer.appendChild(messageDiv);

        // Scroll to latest message
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Close the modal
        let screenshotModal = bootstrap.Modal.getInstance(document.getElementById("screenshot-modal"));
        screenshotModal.hide();
    });

    // Function to close modal manually
    document.getElementById("close-screenshot-modal").addEventListener("click", function () {
        let screenshotModal = bootstrap.Modal.getInstance(document.getElementById("screenshot-modal"));
        screenshotModal.hide();
    });
});


// /stack <query> - find solutions on stackoverflow
document.getElementById("chat-message-input").addEventListener("input", function (e) {
    let inputValue = this.value.trim();
    
    if (inputValue.startsWith("/stack ")) {
        clearTimeout(window.stackTimeout);
        
        window.stackTimeout = setTimeout(() => {
            let query = inputValue.replace("/stack ", "").trim();
            if (query.length > 0) {
                searchStackOverflow(query);
            }
        }, 3000);  // Wait 3 seconds after user stops typing
    }
});

function searchStackOverflow(query) {
    let apiUrl = `https://api.stackexchange.com/2.3/search?order=desc&sort=relevance&intitle=${encodeURIComponent(query)}&site=stackoverflow`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            let resultsList = document.getElementById("stackResultsList");
            resultsList.innerHTML = "";

            if (data.items.length === 0) {
                resultsList.innerHTML = "<p>No results found! 😞</p>";
                return;
            }

            data.items.forEach(item => {
                let listItem = document.createElement("li");

                let questionLink = document.createElement("a");
                questionLink.href = "#";
                questionLink.textContent = item.title;
                questionLink.onclick = function () {
                    fetchStackAnswer(item.question_id);
                };

                listItem.appendChild(questionLink);
                resultsList.appendChild(listItem);
            });

            let modal = new bootstrap.Modal(document.getElementById("stackModal"));
            modal.show();
        })
        .catch(error => console.error("Error fetching Stack Overflow results:", error));
}

function fetchStackAnswer(questionId) {
    let apiUrl = `https://api.stackexchange.com/2.3/questions/${questionId}/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            let answerContainer = document.getElementById("stackAnswerContainer");
            answerContainer.innerHTML = "";

            if (data.items.length === 0) {
                answerContainer.innerHTML = "<p>No answers available! 😞</p>";
                return;
            }

            let bestAnswer = data.items[0].body;
            answerContainer.innerHTML = `
                <div class="answer-box">${bestAnswer}</div>
                <button class="btn btn-primary mt-3" onclick="selectAnswer()">Select</button>
            `;

            let modal = new bootstrap.Modal(document.getElementById("stackAnswerModal"));
            modal.show();
        })
        .catch(error => console.error("Error fetching Stack Overflow answer:", error));
}

function selectAnswer() {
    let answerText = document.querySelector("#stackAnswerContainer .answer-box").innerText.trim();
    let chatInput = document.getElementById("chat-message-input");

    chatInput.value = answerText;
    
    let modal = bootstrap.Modal.getInstance(document.getElementById("stackAnswerModal"));
    modal.hide();
}


// /Screen record /record <time>
let mediaRecorder;
let recordedChunks = [];
let stopTimeout;
let typingTimer;

document.getElementById("chat-message-input").addEventListener("input", function () {
    let inputValue = this.value.trim();

    if (inputValue.startsWith("/record ")) {
        clearTimeout(typingTimer); // Clear previous timer
        typingTimer = setTimeout(() => {
            let args = inputValue.replace("/record ", "").trim();
            let duration = parseInt(args, 10);

            if (isNaN(duration) || duration <= 0) {
                console.log("Invalid recording duration");
                return;
            }

            startScreenRecording(duration);
            this.value = ""; // Clear input after triggering
        }, 3000); // 3-second delay after user stops typing
    }
});

async function startScreenRecording(duration) {
    try {
        const stream = await navigator.mediaDevices.getDisplayMedia({
            video: { mediaSource: "screen" },
            audio: true
        });

        mediaRecorder = new MediaRecorder(stream);
        recordedChunks = [];

        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) recordedChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const recordedBlob = new Blob(recordedChunks, { type: "video/webm" });
            const recordedUrl = URL.createObjectURL(recordedBlob);
            document.getElementById("recordedVideo").src = recordedUrl;

            // Show the modal with the video
            let recordModal = new bootstrap.Modal(document.getElementById("recordModal"));
            recordModal.show();
        };

        mediaRecorder.start();

        // Stop recording after the specified duration
        stopTimeout = setTimeout(() => {
            mediaRecorder.stop();
            stopScreenSharing(stream);
        }, duration * 1000);
    } catch (error) {
        console.error("Error starting screen recording:", error);
    }
}

function stopScreenSharing(stream) {
    stream.getTracks().forEach(track => track.stop());
}

// Download Recording
document.getElementById("downloadRecording").addEventListener("click", function () {
    if (recordedChunks.length === 0) return;

    const recordedBlob = new Blob(recordedChunks, { type: "video/webm" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(recordedBlob);
    a.download = "screen_recording.webm";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});

// Delete Recording
document.getElementById("deleteRecording").addEventListener("click", function () {
    document.getElementById("recordedVideo").src = "";
    recordedChunks = [];
});


// /location - share your live location

document.addEventListener("DOMContentLoaded", function () {
    let typingTimer;
    const inputField = document.getElementById("chat-message-input");

    inputField.addEventListener("keyup", function (event) {
        clearTimeout(typingTimer);
        if (inputField.value.startsWith("/location")) {
            typingTimer = setTimeout(() => {
                getUserLocation();
            }, 3000);  // 3-sec delay to let the user finish typing
        }
    });

    function getUserLocation() {
        if (!navigator.geolocation) {
            alert("Geolocation is not supported by your browser.");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const googleMapsUrl = `https://www.google.com/maps?q=${lat},${lon}`;

                // Update modal content
                document.getElementById("location-map").src = `https://maps.google.com/maps?q=${lat},${lon}&z=15&output=embed`;
                document.getElementById("location-url").value = googleMapsUrl;
                document.getElementById("send-location").setAttribute("data-url", googleMapsUrl);

                // Show modal
                new bootstrap.Modal(document.getElementById("locationModal")).show();
            },
            (error) => {
                alert("Unable to retrieve location. Please allow location access.");
            }
        );
    }

    // Send Location to Chat
    document.getElementById("send-location").addEventListener("click", function () {
        const url = this.getAttribute("data-url");
        const chatInput = document.getElementById("chat-message-input");
        chatInput.value = url;  // Append location to chat input
        chatInput.focus();
        new bootstrap.Modal(document.getElementById("locationModal")).hide();
    });
});



// /security check 
document.addEventListener("DOMContentLoaded", function () {
    let typingTimer;
    const inputField = document.getElementById("chat-message-input");

    inputField.addEventListener("keyup", function () {
        clearTimeout(typingTimer);
        if (inputField.value.trim() === "/security-check") {
            typingTimer = setTimeout(() => {
                startSecurityCheck();
            }, 2000);
        }
    });

    function startSecurityCheck() {
        const securityResult = document.getElementById("security-result");
        securityResult.innerHTML = `
            <div class="scanner-container">
                <div class="scanner-circle">
                    <div class="scanner-inner"></div>
                    <div class="scanning-wave"></div>
                </div>
                <p>🔍 Scanning system for vulnerabilities...</p>
            </div>
        `;

        fetch("/dm/security-check/")
            .then(response => response.json())
            .then(data => {
                setTimeout(() => {
                    securityResult.innerHTML = `
                        <div class="security-report">
                            <h3 class="report-title">🛡 Security Report</h3>
                            <div class="report-section">
                                <p><b>Open Ports:</b> ${data.open_ports.length > 0 ? data.open_ports.join(", ") : "✅ Secure"}</p>
                                <p><b>Outdated Software:</b> ${data.outdated_software.length > 0 ? "⚠️ Needs Update" : "✅ Up-to-date"}</p>
                                <p><b>System Uptime:</b> ${data.system_uptime}</p>
                                <p><b>Suspicious Processes:</b> ${data.suspicious_processes.length > 0 ? "🚨 Threat Detected!" : "✅ No Threats"}</p>
                                <p><b>Network Connections:</b> ${data.network_connections.length > 0 ? "⚠️ Active Connections Found" : "✅ Secure"}</p>
                                <p><b>Firewall Status:</b> ${data.firewall_status.includes("active") ? "✅ Firewall Enabled" : "🚨 Firewall Disabled"}</p>
                                <p><b>Running Services:</b> ${data.running_services.length > 0 ? data.running_services.join(", ") : "✅ Minimal Services Running"}</p>
                                <p><b>File Integrity:</b> ${data.file_integrity.includes("root") ? "⚠️ Changes Detected" : "✅ Files Intact"}</p>
                                <p><b>Rootkit Check:</b> ${data.rootkit_check.includes("INFECTED") ? "🚨 Rootkit Found!" : "✅ System Clean"}</p>
                                <p><b>Unused Users:</b> ${data.unused_users.length > 0 ? "⚠️ Inactive Accounts Found" : "✅ All Active Accounts"}</p>
                                <p><b>Malware Check:</b> ${data.malware ? "🚨 Malware Detected!" : "✅ No Malware Found"}</p>
                            </div>
                            <button class="btn btn-danger scan-fix-btn" id="fix-issues-btn">🛠 Fix Issues</button>
                        </div>
                    `;

                    document.getElementById("fix-issues-btn").addEventListener("click", function () {
                        fetch("/dm/fix-security-issues/", { method: "POST" })
                            .then(response => response.json())
                            .then(data => {
                                alert(data.message);
                                securityResult.innerHTML = `<p class="fixed-message">✅ All security issues fixed!</p>`;
                            });
                    });

                }, 4000);
            });

        new bootstrap.Modal(document.getElementById("securityCheckModal")).show();
    }
});


// /export -- Export the conversation data
document.addEventListener("DOMContentLoaded", function () {
    let typingTimer;
    const inputField = document.getElementById("chat-message-input");

    inputField.addEventListener("keyup", function () {
        clearTimeout(typingTimer);
        if (inputField.value.trim() === "/export") {
            typingTimer = setTimeout(() => {
                showExportModal();
            }, 1000);
        }
    });

    function showExportModal() {
        new bootstrap.Modal(document.getElementById("exportModal")).show();
    }

    document.getElementById("export-btn").addEventListener("click", function () {
        const conversationId = window.djangoData.conversationId;
        const orgId = window.djangoData.orgId;
        const exportType = document.querySelector('input[name="exportType"]:checked').value;
        const customEmail = document.getElementById("custom-email").value;

        document.getElementById("export-status").innerHTML = "⏳ Processing...";

        fetch("/dm/export-messages/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ conversation_id: conversationId, org_id: orgId, export_type: exportType, custom_email: customEmail }),
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("export-status").innerHTML = data.error ? `❌ ${data.error}` : `✅ ${data.message}`;
        })
        .catch(() => {
            document.getElementById("export-status").innerHTML = "❌ Error processing request!";
        });
    });

    document.querySelectorAll('input[name="exportType"]').forEach(input => {
        input.addEventListener("change", function () {
            document.getElementById("custom-email-box").style.display = input.value === "input-email" ? "block" : "none";
        });
    });
});


// /hacker-mode 
document.addEventListener("DOMContentLoaded", function () {
    let typingTimer;
    const inputField = document.getElementById("chat-message-input");

    inputField.addEventListener("keyup", function () {
        clearTimeout(typingTimer);
        if (inputField.value.trim() === "/hacker-mode") {
            typingTimer = setTimeout(() => {
                startHackerMode();
                inputField.value = ""; // Clear input
            }, 1000);
        } else if (inputField.value.trim() === "/exit-hacker-mode") {
            typingTimer = setTimeout(() => {
                stopHackerMode();
                inputField.value = ""; // Clear input
            }, 1000);
        }
    });

    function startHackerMode() {
        let hackerScreen = document.createElement("div");
        hackerScreen.id = "hacker-mode-screen";
        document.body.appendChild(hackerScreen);

        let hackerText = document.createElement("div");
        hackerText.id = "hacker-text";
        hackerScreen.appendChild(hackerText);

        document.body.classList.add("hacker-active");

        // Create Matrix Rain Effect
        let matrixCanvas = document.createElement("canvas");
        matrixCanvas.id = "matrixCanvas";
        hackerScreen.appendChild(matrixCanvas);

        let chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()";
        let hackerInterval = setInterval(() => {
            hackerText.innerHTML = "";
            for (let i = 0; i < 20; i++) {
                let randomCode = "";
                for (let j = 0; j < 50; j++) {
                    randomCode += chars.charAt(Math.floor(Math.random() * chars.length));
                }
                hackerText.innerHTML += `<p>${randomCode}</p>`;
            }
        }, 100);

        hackerScreen.dataset.interval = hackerInterval;

        startMatrixEffect();
    }

    function stopHackerMode() {
        let hackerScreen = document.getElementById("hacker-mode-screen");
        if (hackerScreen) {
            clearInterval(hackerScreen.dataset.interval);
            document.body.classList.remove("hacker-active");
            hackerScreen.remove();
        }
    }

    function startMatrixEffect() {
        let canvas = document.getElementById("matrixCanvas");
        let ctx = canvas.getContext("2d");

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        let letters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        letters = letters.split("");

        let fontSize = 16;
        let columns = canvas.width / fontSize;
        let drops = [];
        for (let x = 0; x < columns; x++) drops[x] = 1;

        function draw() {
            ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = "#00ff00";
            ctx.font = fontSize + "px monospace";

            for (let i = 0; i < drops.length; i++) {
                let text = letters[Math.floor(Math.random() * letters.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);

                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        }
        setInterval(draw, 33);
    }
});


// /panic-delete <minutes>
document.addEventListener("DOMContentLoaded", function () {
    let inputField = document.getElementById("chat-message-input");
    let panicDeleteTimeout;

    inputField.addEventListener("input", function () {
        let inputValue = inputField.value.trim();

        if (inputValue.startsWith("/panic-delete ")) {
            clearTimeout(panicDeleteTimeout); // Clear any previous timeout
            panicDeleteTimeout = setTimeout(() => {
                let minutes = parseInt(inputValue.split(" ")[1]);

                if (!isNaN(minutes) && minutes > 0) {
                    startPanicDelete(minutes);
                    inputField.value = "";  // Clear input field after detecting the command
                }
            }, 2500); // 🔥 1.5 seconds delay before processing
        }
    });

    function startPanicDelete(minutes) {
        let orgId = window.djangoData.orgId;
        let conversationId = window.djangoData.conversationId;
        let csrfToken = getCSRFToken();

        if (!orgId || !conversationId) {
            alert("Missing organization or conversation ID!");
            return;
        }

        if (!csrfToken) {
            alert("CSRF token not found!");
            return;
        }

        showLoadingSpinner();

        fetch("/dm/panic-del/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                "org_id": orgId,
                "conversation_id": conversationId,
                "minutes": minutes
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoadingSpinner();
            if (data.success) {
                removeDeletedMessages(minutes);
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => {
            hideLoadingSpinner();
            console.error("Panic Delete Failed:", error);
        });
    }

    function removeDeletedMessages(minutes) {
        let messages = document.querySelectorAll(".chat-message");
        let now = new Date();

        messages.forEach(msg => {
            let timestamp = new Date(msg.getAttribute("data-timestamp"));
            let diffMinutes = (now - timestamp) / (1000 * 60);

            if (diffMinutes <= minutes) {
                msg.remove();
            }
        });
    }

    function showLoadingSpinner() {
        let spinner = document.createElement("div");
        spinner.id = "loading-spinner";
        spinner.innerHTML = `<div class="spinner"></div>`;
        document.body.appendChild(spinner);
    }

    function hideLoadingSpinner() {
        let spinner = document.getElementById("loading-spinner");
        if (spinner) spinner.remove();
    }

    function getCSRFToken() {
        let token = document.querySelector("[name=csrfmiddlewaretoken]")?.value;
        if (!token) {
            token = document.querySelector("meta[name='csrf-token']")?.getAttribute("content");
        }
        return token || "";
    }
});


// /convert-voice - convert voice to text
document.addEventListener("DOMContentLoaded", function () {
    let inputField = document.getElementById("chat-message-input");

    inputField.addEventListener("keyup", function () {
        if (inputField.value.trim() === "/convert-voice") {
            let modal = new bootstrap.Modal(document.getElementById("voiceModal"));
            modal.show();
            inputField.value = "";
        }
    });

    let mediaRecorder;
    let audioChunks = [];
    let startBtn = document.getElementById("startRecording");
    let stopBtn = document.getElementById("stopRecording");
    let convertBtn = document.getElementById("convertRecording");
    let speechText = document.getElementById("speechText");

    // Start Recording
    startBtn.addEventListener("click", async function () {
        try {
            let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = function (event) {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = function () {
                console.log("🎤 Audio Recorded Successfully!");
            };

            mediaRecorder.start();
            console.log("🎙 Recording Started...");
            startBtn.classList.add("d-none");
            stopBtn.classList.remove("d-none");

        } catch (error) {
            console.error("❌ Microphone Access Error:", error);
            alert("Microphone access failed. Please allow permissions.");
        }
    });

    // Stop Recording
    stopBtn.addEventListener("click", function () {
        if (mediaRecorder) {
            mediaRecorder.stop();
            console.log("🛑 Recording Stopped.");
        }
        stopBtn.classList.add("d-none");
        convertBtn.classList.remove("d-none");
    });

    // Convert Audio to Text
    convertBtn.addEventListener("click", function () {
        let audioBlob = new Blob(audioChunks, { type: "audio/wav" });
        let formData = new FormData();
        formData.append("audio_file", audioBlob);

        fetch("/dm/convert-voice/", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                speechText.innerText = data.transcript;
                console.log("📜 Converted Text:", data.transcript);
            } else {
                alert("Conversion failed!");
            }
        })
        .catch(error => {
            console.error("❌ Conversion Error:", error);
        });
    });
});
