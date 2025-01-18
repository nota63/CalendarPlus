

$(document).ready(function() {
    $('#submit-comment').click(function() {
        var commentText = $('#comment-text').val().trim();
        if (commentText == "") {
            alert("Please write a comment before submitting.");
            return;
        }

        var orgId = $(this).data('org-id');
        var groupId = $(this).data('group-id');
        var taskId = $(this).data('task-id');

        // Construct the URL using JavaScript
        var url = '/tasks/task/' + orgId + '/' + groupId + '/' + taskId + '/add_comment/';

        // Send the comment via AJAX
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'comment': commentText,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(response) {
                // Append new comment to the list
                $('#comments-list').append('<li><strong>' + response.username + ':</strong> ' + response.comment + ' (' + response.created_at + ')</li>');
                showNotification('Comment has been added to your task')

                // Clear the comment text area
                $('#comment-text').val('');
            },
            error: function(xhr, errmsg, err) {
                alert("Error submitting comment. Please try again.");
            }
        });
    });
});


// Handle add note featue
document.getElementById("saveNoteButton").addEventListener("click", function() {
    // Fetch the task ID, org ID, and group ID from template context
    var taskId = '{{ task.id }}';
    var orgId = '{{ org_id }}';
    var groupId = '{{ group_id }}';

    // Get the note content
    var noteContent = document.getElementById("noteText").value;

    if (noteContent.trim() === "") {
        alert("Please enter a note!");
        return;
    }

    // Construct the URL dynamically using JavaScript syntax
    var url = "/tasks/task/" + orgId + "/" + groupId + "/" + taskId + "/add_note/";

    // Send the note via AJAX
    $.ajax({
        type: 'POST',
        url: url,
        data: {
            'note': noteContent,
            'csrfmiddlewaretoken': '{{ csrf_token }}' // CSRF token for security
        },
        success: function(response) {
            // Close the modal
            $('#addNoteModal').modal('hide');

            // Append the new note to the list of notes (or update UI as needed)
            var newNote = "<li><strong>You:</strong> " + response.note + " (" + response.created_at + ")</li>";
            document.querySelector("#taskNotesList").insertAdjacentHTML('beforeend', newNote);
            showNotification("Note is integrated")

            // Clear the textarea
            document.getElementById("noteText").value = "";
        },
        error: function(xhr, status, error) {
            alert("Error while adding note: " + error);
        }
    });
});

// Handle the timer
function toggleTimer() {
    var taskId = '{{ task.id }}';
    var orgId = '{{ org_id }}';
    var groupId = '{{ group_id }}';
    var button = document.getElementById("startStopButton");
    var icon = document.getElementById("timerIcon");
    
    // Check if timer is running by reading button text
    var isRunning = button.innerText.toLowerCase() === "stop timer";

    // Set action to either start or stop based on current button state
    var action = isRunning ? "stop" : "start";

    // Make AJAX request to start/stop timer
    $.ajax({
        type: 'POST',
        url: '/tasks/task/' + orgId + '/' + groupId + '/' + taskId + '/manage_timer/',
        data: {
            'action': action,  // send the action (start/stop)
            'csrfmiddlewaretoken': '{{ csrf_token }}'  // CSRF token for security
        },
        success: function(response) {
            if (response.status === 'started') {
                button.innerText = "Stop Timer";  // Change button text to "Stop Timer"
                icon.classList.remove("bi-play-circle");  // Remove play icon
                icon.classList.add("bi-pause-circle");   // Add pause icon
                startTimerDisplay();  // Start updating the time display
            } else if (response.status === 'stopped') {
                button.innerText = "Start Timer";  // Change button text back to "Start Timer"
                icon.classList.remove("bi-pause-circle");  // Remove pause icon
                icon.classList.add("bi-play-circle");      // Add play icon
                stopTimerDisplay();  // Stop updating the time display
            }
        },
        error: function(xhr, status, error) {
            alert("Error: " + error);
        }
    });
}

function startTimerDisplay() {
    // Implement the timer countdown functionality in real-time
    var timeSpent = document.getElementById("timeSpent");
    var startTime = Date.now();  // Capture the start time when the timer starts
    
    // Update time every second
    var timerInterval = setInterval(function() {
        var elapsedTime = Date.now() - startTime;
        var seconds = Math.floor((elapsedTime / 1000) % 60);
        var minutes = Math.floor((elapsedTime / 60000) % 60);
        var hours = Math.floor((elapsedTime / 3600000) % 24);
        
        // Format time as HH:mm:ss
        timeSpent.innerText = formatTime(hours, minutes, seconds);
    }, 1000);
    
    // Store interval ID to clear it when stopping the timer
    window.timerInterval = timerInterval;
}

function stopTimerDisplay() {
    // Clear the interval and stop updating the time display
    clearInterval(window.timerInterval);
}

function formatTime(hours, minutes, seconds) {
    // Format time to be displayed as HH:mm:ss
    return (hours < 10 ? "0" + hours : hours) + ":" + 
           (minutes < 10 ? "0" + minutes : minutes) + ":" + 
           (seconds < 10 ? "0" + seconds : seconds);
}


// handle the progress

document.getElementById('increaseProgress').addEventListener('click', function () {
    updateProgress(10); // Increase by 10
});

document.getElementById('decreaseProgress').addEventListener('click', function () {
    updateProgress(-10); // Decrease by 10
});

function updateProgress(delta) {
    const progressBar = document.getElementById('progressBar');
    const currentProgress = parseInt(progressBar.getAttribute('aria-valuenow'));
    const newProgress = Math.min(100, Math.max(0, currentProgress + delta)); // Ensure between 0 and 100

    $.ajax({
        type: 'POST',
        url: '/tasks/tasks/{{ org_id }}/{{ group_id }}/{{ task.id }}/update_progress/',
        data: {
            'progress': newProgress,
            'csrfmiddlewaretoken': '{{ csrf_token }}'
        },
        success: function (response) {
            if (response.status === 'success') {
                progressBar.style.width = response.progress + '%';
                progressBar.setAttribute('aria-valuenow', response.progress);
                progressBar.textContent = response.progress + '%';
                showNotification("Progress has been synced")
            } else {
                alert(response.message || 'An error occurred.');
            }
        },
        error: function (xhr, status, error) {
            alert('Error: ' + error);
        }
    });
}

// Handle activity logs

$(document).ready(function () {
    // Handle the click event to open the sidebar
    $('#activityLogsButton').click(function () {
        // Fetch activity logs via AJAX when the sidebar is opened
        var orgId = '{{ org_id }}';
        var groupId = '{{ group_id }}';
        var taskId = '{{ task.id }}';

        $.ajax({
            type: 'GET',
            url: '/tasks/tasks/' + orgId + '/' + groupId + '/' + taskId + '/activity_logs/',
            success: function (response) {
                if (response.status === 'success') {
                    loadActivityLogs(response.activity_logs);
                    showNotification("Activity Logs up and running")
                    // Show the sidebar
                    $('#activityLogsSidebar').css('right', '0');
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function (xhr, status, error) {
                alert('Error fetching activity logs: ' + error);
            }
        });
    });

    // Handle the close button click to hide the sidebar
    $('#closeSidebarButton').click(function () {
        $('#activityLogsSidebar').css('right', '-400px');
    });
    showNotification('Task is fired up and ready')

    // Function to load activity logs into the sidebar
    function loadActivityLogs(logs) {
        var container = $('#activityLogsContainer');
        container.empty();  // Clear any existing logs

        // Loop through and display each log
        logs.forEach(function (log) {
            var logElement = `
                <div class="activity-log">
                    <h5>${log.action}</h5>
                    <p>${log.details}</p>
                    <small>${log.created_at}</small>
                </div>
            `;
            container.append(logElement);
        });
    }
});


// Handle task toggle as completed

document.getElementById('toggleTaskStatus').addEventListener('change', function () {
    const taskId = this.getAttribute('data-task-id');
    const orgId = this.getAttribute('data-org-id');
    const groupId = this.getAttribute('data-group-id');
    const isChecked = this.checked;

    // Determine the action based on the toggle state
    const action = isChecked ? 'completed' : 'pending';

    // Send an AJAX request
    fetch(`/tasks/tasks/${orgId}/${groupId}/${taskId}/toggle_status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(), 
        },
        body: JSON.stringify({ status: action }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update the label text
                document.querySelector('label[for="toggleTaskStatus"]').textContent = 
                    isChecked ? 'Mark as Pending' : 'Mark as Completed';
                    showNotification("Victory achieved")
            } else {
                alert('Failed to update task status.');
                this.checked = !isChecked; // Revert the toggle state
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred.');
            this.checked = !isChecked; // Revert the toggle state
        });
});

// Function to get the CSRF token
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return '';
}

/* Handle add remove tag  */
/* Handle Add/Remove Tag */
// Handle Add Tag Button click
document.getElementById('add-tag-btn').addEventListener('click', function () {
    const taskId = this.getAttribute('data-task-id'); // Fetch task ID
    const orgId = this.getAttribute('data-org-id');  // Fetch org ID
    const groupId = this.getAttribute('data-group-id'); // Fetch group ID

    // Open the modal to choose tags
    $('#addTagModal').modal('show');

    // Ensure we only bind the event handler once
    const saveTagButton = document.getElementById('save-tag-btn');
    saveTagButton.onclick = function () {
        const selectedTag = document.getElementById('tag-select').value; // Get selected tag
        if (!selectedTag) {
            alert('Please select a tag.');
            return;
        }

        // Send an AJAX request to add the tag
        fetch(`/tasks/tasks/${orgId}/${groupId}/${taskId}/update_tags/`, { // Corrected the URL structure
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(), // Ensure you include your CSRF token
            },
            body: JSON.stringify({ action: 'add', tag_name: selectedTag }), // Send action and tag_name
        })
            .then(response => response.json())
            .then(data => {
                if (data.tag_name) { // Check if tag_name exists in the response
                    // Create the new tag element
                    const tagBadge = document.createElement('span');
                    tagBadge.classList.add('badge', 'bg-warning');
                    tagBadge.setAttribute('id', `tag-${data.tag_name}`); // Set id for the tag
                    tagBadge.setAttribute('data-task-id', taskId);
                    tagBadge.setAttribute('data-org-id', orgId);
                    tagBadge.setAttribute('data-group-id', groupId);
                    tagBadge.innerHTML = `
                        ${data.tag_name}
                        <button class="btn btn-sm btn-danger remove-tag" 
                                data-tag="${data.tag_name}" 
                                data-tag-id="${data.tag_name}" 
                                data-task-id="${taskId}" 
                                data-org-id="${orgId}" 
                                data-group-id="${groupId}">-</button>
                    `;

                    // Append the new tag to the tag container dynamically
                    const tagContainer = document.querySelector('p');
                    if (tagContainer) {
                        // If there's an existing "No tags" message, remove it
                        const noTagsElement = tagContainer.querySelector('.badge.bg-secondary');
                        if (noTagsElement) {
                            noTagsElement.remove(); // Remove "No tags" message
                        }

                        // Insert the new tag badge before the "+" button
                        const addTagButton = tagContainer.querySelector('#add-tag-btn');
                        if (addTagButton) {
                            tagContainer.insertBefore(tagBadge, addTagButton);
                        } else {
                            // If no "+" button, append it to the end
                            tagContainer.appendChild(tagBadge);
                        }
                    }

                    // Show success notification
                    showNotification('Your task has been tagged!');

                    // Close the modal
                    $('#addTagModal').modal('hide');
                } else {
                    alert('Failed to add tag.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred.');
            });
    };
});


// Remove tag event listener (Improved delegation)
document.addEventListener('click', function (event) {
    if (event.target && event.target.classList.contains('remove-tag')) {
        // Make sure the event is triggered by the button with class 'remove-tag'
        
        const tagElement = event.target.closest('.badge');  // Find the parent badge element
        const taskId = tagElement.getAttribute('data-task-id');  // Fetch task ID from the badge parent
        const orgId = tagElement.getAttribute('data-org-id');  // Fetch org ID from the badge parent
        const groupId = tagElement.getAttribute('data-group-id');  // Fetch group ID from the badge parent
        const tagName = event.target.getAttribute('data-tag');  // Fetch tag name
        
        // Send an AJAX request to remove the tag
        fetch(`/tasks/tasks/${orgId}/${groupId}/${taskId}/update_tags/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ action: 'remove', tag_name: tagName }),  // Send action and tag_name
        })
        .then(response => response.json())
        .then(data => {
            if (data.tag_name) {  // Check if tag_name exists in the response
                // Remove the tag from the displayed list
                tagElement.remove();
                showNotification('Tag removed successfully','success');  // Remove the tag element from the DOM
            } else {
                alert('Failed to remove tag.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred.');
        });
    }
});

// Handle time tracking
// Stopwatch Variables
let stopwatchInterval;
let isRunning = false;
let startTime = 0;
let elapsedTime = 0;

// DOM elements for stopwatch
const startStopBtn = document.getElementById('start-stop-btn');
const resetBtn = document.getElementById('reset-btn');  // Ensure this button exists or add it if needed
const timeDisplay = document.getElementById('time-display');

// Capture dynamic task ID, org ID, and group ID from button attributes
const taskId = startStopBtn.getAttribute('data-task-id');
const orgId = startStopBtn.getAttribute('data-org-id');
const groupId = startStopBtn.getAttribute('data-group-id');

// Function to format time (HH:MM:SS)
function formatTime(time) {
    const hours = Math.floor(time / 3600);
    const minutes = Math.floor((time % 3600) / 60);
    const seconds = time % 60;

    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// Function to start/stop the stopwatch
function toggleStopwatch() {
    if (isRunning) {
        // Stop the stopwatch
        clearInterval(stopwatchInterval);
        startStopBtn.textContent = 'Start';
        saveTime();  // Save the time once stopped
    } else {
        // Start the stopwatch
        startTime = Date.now() - elapsedTime;
        stopwatchInterval = setInterval(updateTimeDisplay, 1000);
        startStopBtn.textContent = 'Stop';
    }
    isRunning = !isRunning;
    showNotification('Stopwatch in action, logging your activity time. It will keep going until you stop it')
}

// Function to update time display
function updateTimeDisplay() {
    elapsedTime = Date.now() - startTime;
    timeDisplay.textContent = formatTime(elapsedTime / 1000);  // Convert to seconds
}

// Function to reset the stopwatch
function resetStopwatch() {
    clearInterval(stopwatchInterval);
    isRunning = false;
    startStopBtn.textContent = 'Start';
    timeDisplay.textContent = '00:00:00';
    elapsedTime = 0;
}

// Function to save time to the database and append it dynamically
// Function to save time to the database
function saveTime() {
    const timeSpent = (elapsedTime / 1000 / 3600).toFixed(2); // Convert to hours

    // Send AJAX request to save time
    fetch(`/tasks/tasks/${orgId}/${groupId}/${taskId}/save_time/`, {  // Correct URL structure
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),  // Ensure CSRF token is included
        },
        body: JSON.stringify({
            time_spent: timeSpent,  // Send time spent in hours
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            
            showNotification("Time logged with precision")
            
            
            // Dynamically create a new badge for the new time entry
            const newBadge = document.createElement('span');
            newBadge.classList.add('badge', 'bg-info');
            newBadge.setAttribute('id', `time-entry-${data.time_entry_id}`); // Set unique ID for the time entry badge
            newBadge.setAttribute('data-task-id', taskId);
            newBadge.setAttribute('data-org-id', orgId);
            newBadge.setAttribute('data-group-id', groupId);
            newBadge.textContent = `${data.username}: ${data.time_spent} hours`;

            // Append the new badge to the time tracking section
            const timeTrackingContainer = document.querySelector('p');
            if (timeTrackingContainer) {
                const noTimeElement = timeTrackingContainer.querySelector('.badge.bg-secondary');
                if (noTimeElement) {
                    noTimeElement.remove(); // Remove "No time tracked" message
                }
                timeTrackingContainer.appendChild(newBadge);  // Append the new time entry
            }

            // Optionally reset stopwatch after saving time
            resetStopwatch();
        } else {
            alert('Failed to save time.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while saving the time.');
    });
}

// Event listeners for buttons


document.addEventListener('DOMContentLoaded', function () {
    const raiseProblemButton = document.getElementById('raise-problem-btn');
    const loadingSpinner = document.getElementById('loading-spinner'); // Spinner element
    const loadingText = document.getElementById('loading-text'); // Loading text element

    if (raiseProblemButton) {
        raiseProblemButton.addEventListener('click', function () {
            const orgId = this.getAttribute('data-org-id');
            const groupId = this.getAttribute('data-group-id');
            const taskId = this.getAttribute('data-task-id');
            const problemDescription = document.getElementById('problem-description').value;

            if (!problemDescription) {
                alert('Please provide a description for the problem.');
                return;
            }

            // Show the spinner and text
            loadingSpinner.style.display = 'inline-block';
            loadingText.style.display = 'inline-block';

            // Send an AJAX request to report the problem
            fetch(`/tasks/tasks/${orgId}/${groupId}/${taskId}/create_problem/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(), // Ensure CSRF token is added here
                },
                body: JSON.stringify({
                    description: problemDescription,
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                   
                    showNotification('Issue escalated and flagged to your manager')
                      

                    // Create a new list item for the reported problem
                    const newProblemItem = document.createElement('li');
                    newProblemItem.innerHTML = `
                        <strong>${data.reported_by}</strong>: 
                        ${data.description} 
                        (${new Date(data.created_at).toLocaleString()}) 
                        <strong>Is Resolved: ${data.is_resolved}</strong>
                    `;

                    // Append the new problem to the list
                    const problemsList = document.getElementById('problems-list');
                    if (problemsList) {
                        problemsList.appendChild(newProblemItem);
                     
                        // Trigger the animation
                        setTimeout(function () {
                            newProblemItem.classList.add('show');
                        }, 10); // Adding a small delay to trigger the transition
                    }

                    // Optionally, clear the problem description textarea
                    document.getElementById('problem-description').value = '';
                } else {
                    alert('Failed to report the problem.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while reporting the problem.');
            })
            .finally(() => {
                // Hide the spinner and text once the request is complete
                loadingSpinner.style.display = 'none';
                loadingText.style.display = 'none';
            });
        });
    } else {
        console.error('Raise Problem button not found');
    }
});

// Function to get CSRF token from the cookies
function getCSRFToken() {
    let csrfToken = null;
    const cookieValue = document.cookie.split(';').find(cookie => cookie.trim().startsWith('csrftoken='));
    if (cookieValue) {
        csrfToken = cookieValue.split('=')[1];
    }
    return csrfToken;
}



// Handle problem resolve
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.resolve-problem-btn').forEach(button => {
        button.addEventListener('click', function () {
            const orgId = this.getAttribute('data-org-id');
            const groupId = this.getAttribute('data-group-id');
            const taskId = this.getAttribute('data-task-id');
            const problemId = this.getAttribute('data-problem-id');

            console.log(`Resolving problem with orgId=${orgId}, groupId=${groupId}, taskId=${taskId}, problemId=${problemId}`);

            // Reference to the current list item
            const problemListItem = this.closest('li');
            if (!problemListItem) {
                console.error("Problem list item not found!");
                return;
            }

            fetch(`/tasks/tasks/${orgId}/${groupId}/${taskId}/resolve_problem/${problemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Server response:", data);
                if (data.success) {
                    // Display notification
                    showNotification(data.success);

                    // Update the Is Resolved field in the UI
                    const isResolvedField = problemListItem.querySelector('strong:nth-of-type(2)');
                    if (isResolvedField) {
                        isResolvedField.textContent = 'Is Resolved: True';
                    } else {
                        console.warn("Is Resolved field not found!");
                    }

                    // Remove the resolve button
                    const resolveButton = problemListItem.querySelector('.resolve-problem-btn');
                    if (resolveButton) {
                        resolveButton.remove();
                    } else {
                        console.warn("Resolve button not found!");
                    }
                } else {
                    alert('Failed to mark the problem as resolved.');
                    console.error("Error response from server:", data);
                }
            })
            .catch(error => {
                console.error('Error occurred:', error);
                alert('An error occurred while resolving the problem.');
            });
        });
    });
});

// Function to show notification
function showNotification(message) {
    const notification = document.getElementById('notification');
    const notificationText = document.getElementById('notification-text');
    notificationText.textContent = message;
    notification.classList.add('show');

    // Auto hide notification after 3 seconds
    setTimeout(() => {
        closeNotification();
    }, 5000);
}

// Function to close the notification
function closeNotification() {
    const notification = document.getElementById('notification');
    notification.classList.remove('show');
}

// Function to get CSRF token from cookies
function getCSRFToken() {
    let csrfToken = null;
    const cookieValue = document.cookie.split(';').find(cookie => cookie.trim().startsWith('csrftoken='));
    if (cookieValue) {
        csrfToken = cookieValue.split('=')[1];
    }
    return csrfToken;
}


// Handle note deletion
document.addEventListener('DOMContentLoaded', function () {
    // Add event listener for delete buttons
    document.querySelectorAll('.delete-note').forEach(button => {
        button.addEventListener('click', function () {
            const noteId = this.getAttribute('data-note-id');
            const taskId = this.getAttribute('data-task-id');
            const groupId = this.getAttribute('data-group-id');
            const orgId = this.getAttribute('data-org-id');

            // Send AJAX request to delete the note
            fetch(`/tasks/tasks/${orgId}/${groupId}/${taskId}/${noteId}/delete_note/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'), // Ensure CSRF token is included
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    // Remove the note element from the DOM
                    const noteElement = document.getElementById(`note-${noteId}`);
                    if (noteElement) {
                        noteElement.remove();
                    }
                   
                    showNotification("Note has been expunged and is no longer available.")
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

// Function to get the CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



// Edit the note
document.addEventListener('DOMContentLoaded', function () {
    // Function to get CSRF token from the cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Handle Edit button click
    document.querySelectorAll('.edit-note').forEach(button => {
        button.addEventListener('click', function () {
            const noteId = this.getAttribute('data-note-id');
            const taskId = this.getAttribute('data-task-id');
            const groupId = this.getAttribute('data-group-id');
            const orgId = this.getAttribute('data-org-id');
            const currentNoteContent = this.getAttribute('data-note-content');
            
            // Populate the modal with the current note content
            document.getElementById('noteContent').value = currentNoteContent;

            // Show the modal
            const editModal = new bootstrap.Modal(document.getElementById('editNoteModal'));
            editModal.show();

            // Set a save handler for the modal save button
            document.getElementById('saveNoteBtn').addEventListener('click', function () {
                const updatedNoteContent = document.getElementById('noteContent').value;

                fetch(`/tasks/tasks/${orgId}/${groupId}/${taskId}/${noteId}/edit_note/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        'note': updatedNoteContent
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        // Find the note item by ID and update the content
                        const noteItem = document.getElementById(`note-${noteId}`);
                        if (noteItem) {
                            const noteContentElement = noteItem.querySelector('.note-content');
                            if (noteContentElement) {
                                noteContentElement.textContent = updatedNoteContent;
                            }
                        }

                        
                        showNotification('Your note has been revised and the updates are now logged')

                        // Close the modal
                        var modal = bootstrap.Modal.getInstance(document.getElementById('editNoteModal'));
                        modal.hide();
                    } else {
                        alert(data.error);
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        });
    });
});




// stopwatrch functions
startStopBtn.addEventListener('click', toggleStopwatch);
resetBtn.addEventListener('click', resetStopwatch);