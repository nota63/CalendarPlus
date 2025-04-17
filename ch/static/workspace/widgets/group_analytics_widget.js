function fetchAndDisplayGroups(orgId) {
    const container = document.getElementById('group-analytics-widget');
    container.innerHTML = `<p class="text-sm text-gray-500 flex items-center justify-center py-4">
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Loading groups...
    </p>`;
    
    fetch(`/admin_widgets/list-groups/${orgId}/`)
        .then(response => response.json())
        .then(data => {
            container.innerHTML = '';
            
            // Create a scrollable container with hidden scrollbar
            const scrollContainer = document.createElement('div');
            scrollContainer.className = 'max-h-80 overflow-y-auto pr-1 scrollbar-hide';
            
            // Add custom scrollbar style
            const style = document.createElement('style');
            style.textContent = `
                .scrollbar-hide::-webkit-scrollbar {
                    width: 6px;
                    background: transparent;
                }
                .scrollbar-hide::-webkit-scrollbar-thumb {
                    background: rgba(203, 213, 225, 0.5);
                    border-radius: 10px;
                }
                .scrollbar-hide:hover::-webkit-scrollbar-thumb {
                    background: rgba(203, 213, 225, 0.8);
                }
                .scrollbar-hide {
                    scrollbar-width: thin;
                    scrollbar-color: rgba(203, 213, 225, 0.5) transparent;
                }
            `;
            container.appendChild(style);
            
            if (data.groups && data.groups.length > 0) {
                const groupList = document.createElement('div');
                groupList.className = 'space-y-1';  // Tighter spacing for ClickUp-like density
                
                data.groups.forEach(group => {
                    const groupRow = document.createElement('div');
                    groupRow.className = `
                        flex items-center justify-between p-3 rounded-md
                        hover:bg-indigo-50 transition-all duration-150 cursor-pointer
                        border border-transparent hover:border-indigo-100
                        group-row shadow-sm hover:shadow
                    `;
                    groupRow.dataset.groupId = group.id;
                    
                    groupRow.innerHTML = `
                        <div class="flex items-center flex-1 min-w-0">
                            <div class="w-8 h-8 rounded-md mr-3 bg-indigo-100 flex-shrink-0 overflow-hidden">
                                <img src="${group.team_leader.profile_picture || '/static/default-profile-pic.jpg'}"
                                     alt="${group.team_leader.username}"
                                     class="w-full h-full object-cover">
                            </div>
                            <div class="truncate">
                                <p class="text-sm font-medium text-gray-800 truncate">${group.group_name}</p>
                                <p class="text-xs text-gray-500 flex items-center">
                                    <span class="truncate">${group.team_leader.username}</span>
                                    <span class="mx-1">•</span>
                                    <span class="text-gray-400">Team Lead</span>
                                </p>
                            </div>
                        </div>
                        <div class="flex-shrink-0 ml-2 text-indigo-600">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5 opacity-60 group-hover:opacity-100 transition-opacity">
                                <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
                            </svg>
                        </div>
                    `;
                    
                    groupRow.addEventListener('click', () => fetchGroupAnalytics(group.id, orgId));
                    
                    groupList.appendChild(groupRow);
                });
                
                scrollContainer.appendChild(groupList);
                container.appendChild(scrollContainer);
            } else {
                container.innerHTML = `
                    <div class="flex flex-col items-center justify-center py-8 text-center">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="w-10 h-10 text-gray-300 mb-3">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M18 18v2a2 2 0 01-2 2H8a2 2 0 01-2-2v-2M12 2a5 5 0 00-5 5v3h10V7a5 5 0 00-5-5z" />
                        </svg>
                        <p class="text-sm text-gray-500">No groups found for this organization.</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Failed to fetch group leader info:', error);
            container.innerHTML = `
                <div class="flex flex-col items-center justify-center py-8 text-center">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" class="w-10 h-10 text-red-400 mb-3">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <p class="text-sm text-red-500">Failed to load groups. Please try again later.</p>
                </div>
            `;
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
