function fetchAndDisplayGroups(orgId) {
    const container = document.getElementById('group-analytics-widget');
    container.innerHTML = `<p>Loading groups...</p>`;  // Show loading text initially

    // Fetch group leader info from the server
    fetch(`/admin_widgets/list-groups/${orgId}/`)  // Replace with the correct URL
        .then(response => response.json())
        .then(data => {
            container.innerHTML = '';  // Clear existing content

            // Check if groups are available
            if (data.groups && data.groups.length > 0) {
                data.groups.forEach(group => {
                    const groupCard = document.createElement('div');
                    groupCard.className = 'group-card p-4 mb-4 rounded-xl border shadow bg-white';
                    groupCard.dataset.groupId = group.id;  // Store group ID for later use

                    // Create the group leader card content
                    groupCard.innerHTML = `
                        <h2 class="text-xl font-bold mb-2">${group.group_name}</h2>
                        <div class="flex items-center mb-3">
                            <img src="${group.team_leader.profile_picture || '/static/default-profile-pic.jpg'}" 
                                 alt="${group.team_leader.username}" 
                                 class="w-12 h-12 rounded-full mr-3">
                            <div>
                                <p class="font-semibold">${group.team_leader.username}</p>
                                <p class="text-gray-600 text-sm">Team Leader</p>
                            </div>
                        </div>
                    `;

                    // Add event listener for click to fetch analytics
                    groupCard.addEventListener('click', () => fetchGroupAnalytics(group.id, orgId));

                    container.appendChild(groupCard);
                });
            } else {
                container.innerHTML = `<p>No groups found for this organization.</p>`;
            }
        })
        .catch(error => {
            console.error('Failed to fetch group leader info:', error);
            container.innerHTML = `<p class="text-red-600">Failed to load groups. Please try again later.</p>`;
        });
}

function fetchGroupAnalytics(groupId, orgId) {
    // Make the AJAX request to fetch group analytics
    fetch(`/admin_widgets/group-analytics-widget/${orgId}/${groupId}/`)
        .then(response => response.json())
        .then(data => {
            displayGroupAnalyticsModal(data.group_analytics);
        })
        .catch(error => {
            console.error('Failed to fetch group analytics:', error);
        });
}

function displayGroupAnalyticsModal(analytics) {
    // Create a modal element dynamically
    const modal = document.createElement('div');
    modal.className = 'modal fade show';
    modal.style.display = 'block';  // Make modal visible
    modal.tabIndex = -1;
    modal.setAttribute('aria-labelledby', 'exampleModalLabel');
    modal.setAttribute('aria-hidden', 'true');

    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="exampleModalLabel">${analytics.group_name} Analytics</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <h6>Total Tasks: ${analytics.total_tasks}</h6>
                    <p>Completed Tasks: ${analytics.completed_tasks}</p>
                    <p>In Progress Tasks: ${analytics.in_progress_tasks}</p>
                    <p>Pending Tasks: ${analytics.pending_tasks}</p>
                    <p>Cancelled Tasks: ${analytics.cancelled_tasks}</p>
                    <p>Tasks Need Changes: ${analytics.need_changes}</p>
                    <p>Pending Approval: ${analytics.pending_approval}</p>
                    <p>Overdue Tasks: ${analytics.overdue_tasks_count}</p>
                    <p>Urgent Tasks: ${analytics.urgent_tasks_count}</p>
                    <p>Progress: ${analytics.progress_percent}%</p>
                    <p>Next Deadline: ${analytics.next_deadline ? analytics.next_deadline : 'N/A'}</p>
                    <p>Latest Deadline: ${analytics.latest_deadline ? analytics.latest_deadline : 'N/A'}</p>
                    <p>Active Members: ${analytics.active_members_count}</p>

                    <h6>Top Contributors</h6>
                    <ul>
                        ${analytics.top_contributors.map(contributor => `
                            <li>${contributor.username}: ${contributor.completed_tasks} completed tasks</li>
                        `).join('')}
                    </ul>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;

    // Append modal to the body
    document.body.appendChild(modal);

    // Close the modal when the background is clicked (optional)
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            document.body.removeChild(modal);  // Remove the modal from the DOM
        }
    });

    // Optionally, hide the modal after closing using Bootstrap's modal functionality
    const modalElement = new bootstrap.Modal(modal);
    modalElement.show();
}
