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
    <div class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black bg-opacity-50">
      <div class="w-full max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-xl overflow-hidden">
        <div class="flex flex-col">
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center">
              <div class="w-2 h-6 bg-blue-500 rounded-full mr-3"></div>
              <h5 class="text-xl font-semibold text-gray-800 dark:text-white">${analytics.group_name} Analytics</h5>
            </div>
            <button type="button" class="text-gray-400 hover:text-gray-500 focus:outline-none" data-bs-dismiss="modal" aria-label="Close">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <!-- Content -->
          <div class="p-6">
            <!-- Progress Summary Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div class="bg-white dark:bg-gray-700 rounded-lg shadow p-4 border-l-4 border-blue-500">
                <p class="text-sm text-gray-500 dark:text-gray-400">Total Tasks</p>
                <h3 class="text-2xl font-bold text-gray-800 dark:text-white">${analytics.total_tasks}</h3>
              </div>
              <div class="bg-white dark:bg-gray-700 rounded-lg shadow p-4 border-l-4 border-green-500">
                <p class="text-sm text-gray-500 dark:text-gray-400">Completed</p>
                <h3 class="text-2xl font-bold text-gray-800 dark:text-white">${analytics.completed_tasks}</h3>
              </div>
              <div class="bg-white dark:bg-gray-700 rounded-lg shadow p-4 border-l-4 border-yellow-500">
                <p class="text-sm text-gray-500 dark:text-gray-400">In Progress</p>
                <h3 class="text-2xl font-bold text-gray-800 dark:text-white">${analytics.in_progress_tasks}</h3>
              </div>
              <div class="bg-white dark:bg-gray-700 rounded-lg shadow p-4 border-l-4 border-red-500">
                <p class="text-sm text-gray-500 dark:text-gray-400">Overdue</p>
                <h3 class="text-2xl font-bold text-gray-800 dark:text-white">${analytics.overdue_tasks_count}</h3>
              </div>
            </div>
            
            <!-- Main Content -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Left Column -->
              <div class="bg-white dark:bg-gray-700 rounded-lg shadow p-6">
                <h6 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">Task Status</h6>
                
                <!-- Progress bar -->
                <div class="mb-4">
                  <div class="flex justify-between mb-1">
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Progress</span>
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">${analytics.progress_percent}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-600">
                    <div class="bg-blue-600 h-2.5 rounded-full" style="width: ${analytics.progress_percent}%"></div>
                  </div>
                </div>
                
                <!-- Status grid -->
                <div class="grid grid-cols-2 gap-4">
                  <div class="flex items-center space-x-2">
                    <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <span class="text-sm text-gray-600 dark:text-gray-300">Pending: ${analytics.pending_tasks}</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <div class="w-3 h-3 rounded-full bg-red-500"></div>
                    <span class="text-sm text-gray-600 dark:text-gray-300">Cancelled: ${analytics.cancelled_tasks}</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <div class="w-3 h-3 rounded-full bg-orange-500"></div>
                    <span class="text-sm text-gray-600 dark:text-gray-300">Need Changes: ${analytics.need_changes}</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <div class="w-3 h-3 rounded-full bg-purple-500"></div>
                    <span class="text-sm text-gray-600 dark:text-gray-300">Pending Approval: ${analytics.pending_approval}</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <div class="w-3 h-3 rounded-full bg-blue-500"></div>
                    <span class="text-sm text-gray-600 dark:text-gray-300">Urgent: ${analytics.urgent_tasks_count}</span>
                  </div>
                </div>
              </div>
              
              <!-- Right Column -->
              <div class="bg-white dark:bg-gray-700 rounded-lg shadow p-6">
                <h6 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">Team Metrics</h6>
                
                <!-- Team stats -->
                <div class="space-y-4">
                  <div class="flex justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-300">Active Members</span>
                    <span class="text-sm font-medium text-gray-800 dark:text-white">${analytics.active_members_count}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-300">Next Deadline</span>
                    <span class="text-sm font-medium text-gray-800 dark:text-white">${analytics.next_deadline ? analytics.next_deadline : 'N/A'}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-sm text-gray-600 dark:text-gray-300">Latest Deadline</span>
                    <span class="text-sm font-medium text-gray-800 dark:text-white">${analytics.latest_deadline ? analytics.latest_deadline : 'N/A'}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Top Contributors Section -->
            <div class="mt-6 bg-white dark:bg-gray-700 rounded-lg shadow p-6">
              <h6 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">Top Contributors</h6>
              <div class="space-y-3">
                ${analytics.top_contributors.map(contributor => `
                  <div class="flex items-center justify-between">
                    <div class="flex items-center">
                      <div class="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-500 dark:text-blue-300 font-semibold">
                        ${contributor.username.charAt(0).toUpperCase()}
                      </div>
                      <span class="ml-3 text-gray-700 dark:text-gray-300">${contributor.username}</span>
                    </div>
                    <div class="flex items-center">
                      <span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                        ${contributor.completed_tasks} tasks
                      </span>
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>
          </div>
          
          <!-- Footer -->
          <div class="px-6 py-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 flex justify-end">
            <button type="button" class="px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600" data-bs-dismiss="modal">Close</button>
            <button type="button" class="ml-3 px-4 py-2 bg-blue-600 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-blue-700 dark:hover:bg-blue-600">Export</button>
          </div>
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
