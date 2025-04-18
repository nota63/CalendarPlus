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


// # Widget 2) Group Task completion velocity-----------------------------------------------------------------------------------------------------
let groupVelocityChartInstance;

async function groupTasksVelocity(orgId) {
  // Keep the original URL construction exactly as it was
  const url = `/admin_widgets/group-task-completion-velocity/${orgId}/`;
  
  // Create a container with proper styling if it doesn't exist
  let containerEl = document.getElementById("velocityChartContainer");
  if (!containerEl) {
    const parentEl = document.querySelector("#chart-section") || document.body;
    containerEl = document.createElement("div");
    containerEl.id = "velocityChartContainer";
    containerEl.className = "bg-white rounded-lg shadow-lg p-6 mb-8 border border-gray-100";
    parentEl.appendChild(containerEl);
    
    // Create header section
    const headerEl = document.createElement("div");
    headerEl.className = "flex items-center justify-between mb-4";
    headerEl.innerHTML = `
      <div>
        <h3 class="text-lg font-semibold text-gray-800">Team Velocity</h3>
        <p class="text-sm text-gray-500">Tasks completed over time by team</p>
      </div>
      <div class="flex space-x-2">
        <button id="velocity30Days" class="px-3 py-1 text-xs font-medium rounded-md bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors">30 Days</button>
        <button id="velocity90Days" class="px-3 py-1 text-xs font-medium rounded-md bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors">90 Days</button>
        <button id="velocityAllTime" class="px-3 py-1 text-xs font-medium rounded-md bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors">All Time</button>
      </div>
    `;
    containerEl.appendChild(headerEl);
    
    // Add event listeners for time period buttons
    const buttons = headerEl.querySelectorAll("button");
    buttons.forEach(btn => {
      btn.addEventListener("click", () => {
        // Reset all buttons
        buttons.forEach(b => {
          b.classList.remove("bg-indigo-50", "text-indigo-600");
          b.classList.add("bg-gray-100", "text-gray-600");
        });
        // Highlight active button
        btn.classList.remove("bg-gray-100", "text-gray-600");
        btn.classList.add("bg-indigo-50", "text-indigo-600");
        
        // In a real app, you would reload data with the correct time period
        // For now we'll just refresh the current data
        if (groupVelocityChartInstance) {
          groupVelocityChartInstance.destroy();
          groupTasksVelocity(orgId);
        }
      });
    });
    
    // Create chart wrapper
    const chartWrapper = document.createElement("div");
    chartWrapper.className = "relative h-64 md:h-80";
    chartWrapper.innerHTML = `
      <canvas id="groupTaskVelocityChart" class="w-full h-full"></canvas>
      <div id="chartLoader" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80 hidden">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    `;
    containerEl.appendChild(chartWrapper);

    // Create chart legend container (will be populated by Chart.js)
    const legendWrapper = document.createElement("div");
    legendWrapper.className = "mt-4 flex flex-wrap items-center justify-center gap-x-6 gap-y-2";
    legendWrapper.id = "customChartLegend";
    containerEl.appendChild(legendWrapper);
  }

  // Keep the original chart element selection exactly as it was
  const chartEl = document.getElementById("groupTaskVelocityChart");
  const loaderEl = document.getElementById("chartLoader");

  if (!chartEl) {
    console.warn("Chart canvas not found.");
    return;
  }

  try {
    // Show loading state
    if (loaderEl) loaderEl.classList.remove("hidden");
    else chartEl.parentElement.classList.add("opacity-50"); // Fallback to original opacity method

    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to fetch velocity data.");

    const data = await response.json();
    const series = data.series || [];

    if (!series.length) {
      chartEl.parentElement.innerHTML = `
        <div class="flex flex-col items-center justify-center h-full">
          <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <p class="mt-2 text-sm font-medium text-gray-500">No task data available yet</p>
        </div>
      `;
      return;
    }

    // Destroy previous chart - keeping original logic
    if (groupVelocityChartInstance) {
      groupVelocityChartInstance.destroy();
    }

    // Define a more modern color palette
    const modernPalette = [
      '#6366f1', // indigo
      '#10b981', // emerald
      '#f59e0b', // amber
      '#ec4899', // pink
      '#8b5cf6', // violet
      '#14b8a6', // teal
      '#f43f5e', // rose
      '#0ea5e9', // sky
      '#a855f7', // purple
      '#84cc16', // lime
    ];

    // Create datasets for Chart.js with improved styling
    // But keep the original data mapping intact
    const datasets = series.map((group, idx) => {
      const color = getColor(idx); // Use the original color function
      return {
        label: group.group_name,
        data: group.data.map(d => ({ x: d.x, y: d.y })),
        borderColor: color,
        backgroundColor: color + "20", // More transparent
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 3,
        pointBackgroundColor: color,
        pointBorderColor: '#fff',
        pointBorderWidth: 1,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: color,
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2
      };
    });

    // Custom tooltip styling
    const customTooltip = {
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      titleColor: '#1f2937',
      bodyColor: '#4b5563',
      bodyFont: {
        family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
        size: 12
      },
      titleFont: {
        family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
        size: 13,
        weight: 'bold'
      },
      borderColor: 'rgba(0, 0, 0, 0.1)',
      borderWidth: 1,
      cornerRadius: 6,
      padding: 12,
      boxPadding: 6,
      usePointStyle: true,
      caretSize: 6,
      caretPadding: 8
    };

    // Draw new chart with improved styling
    groupVelocityChartInstance = new Chart(chartEl, {
      type: 'line',
      data: {
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index'
        },
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'day',
              tooltipFormat: 'MMM d, yyyy'
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)',
              drawBorder: false
            },
            ticks: {
              font: {
                family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
                size: 11
              },
              color: '#6b7280'
            },
            title: {
              display: true,
              text: 'Date',
              font: {
                family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
                size: 12
              },
              color: '#4b5563'
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)',
              drawBorder: false
            },
            ticks: {
              font: {
                family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
                size: 11
              },
              color: '#6b7280',
              precision: 0
            },
            title: {
              display: true,
              text: 'Tasks Completed',
              font: {
                family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
                size: 12
              },
              color: '#4b5563'
            }
          }
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              font: {
                family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
                size: 11
              },
              color: '#4b5563',
              usePointStyle: true,
              boxWidth: 8,
              padding: 15
            }
          },
          tooltip: {
            ...customTooltip,
            callbacks: {
              title: (items) => {
                if (!items.length) return '';
                const date = new Date(items[0].parsed.x);
                return date.toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric',
                  year: 'numeric'
                });
              },
              label: (context) => {
                const label = context.dataset.label || '';
                const value = context.parsed.y;
                return `${label}: ${value} ${value === 1 ? 'task' : 'tasks'}`;
              }
            }
          }
        }
      }
    });

  } catch (error) {
    console.error("Error loading task velocity:", error);
    chartEl.parentElement.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full">
        <svg class="w-12 h-12 text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
        </svg>
        <p class="mt-2 text-sm font-medium text-gray-500">Error loading chart data</p>
        <button class="mt-3 px-4 py-2 text-xs font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 transition-colors" onclick="groupTasksVelocity('${orgId}')">Try Again</button>
      </div>
    `;
  } finally {
    // Hide loading state - maintain both methods
    if (loaderEl) loaderEl.classList.add("hidden");
    chartEl.parentElement.classList.remove("opacity-50"); // Original opacity method
  }
}

// Keep the original color function intact
function getColor(index) {
  const palette = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#0ea5e9'];
  return palette[index % palette.length];
}

// Add this to ensure fonts are loaded
document.head.insertAdjacentHTML('beforeend', `
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    #velocityChartContainer {
      transition: all 0.2s ease;
    }
    #velocityChartContainer:hover {
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
  </style>
`);

// Widget 3) Assign task---------------------------------------------------------------------------
// Function to fetch assignable groups
async function AssignableGroups(orgId) {
  const targetEl = document.getElementById("assignableGroupsList");
  if (!targetEl) return;

  try {
    targetEl.innerHTML = `<p class="text-sm text-gray-400">Fetching groups...</p>`;
    const res = await fetch(`/admin_widgets/get-assignable-groups/${orgId}/`);
    if (!res.ok) throw new Error("Failed to fetch groups");

    const data = await res.json();
    const groups = data.groups || [];

    if (!groups.length) {
      targetEl.innerHTML = `<p class="text-sm text-gray-400">No groups available yet.</p>`;
      return;
    }

    const html = groups.map(g => `
      <div class="px-3 py-2 border border-gray-200 rounded hover:bg-gray-50 cursor-pointer group-item" data-group-id="${g.id}" data-group-name="${g.name}">
        <p class="text-sm font-medium text-gray-700">${g.name}</p>
      </div>
    `).join("");

    targetEl.innerHTML = html;

    // Bind click events to open modal
    document.querySelectorAll(".group-item").forEach(item => {
      item.addEventListener("click", () => {
        const groupId = item.dataset.groupId;
        const groupName = item.dataset.groupName;
        showAssignTaskModal(orgId, groupId, groupName);
      });
    });

  } catch (err) {
    console.error("Error loading groups:", err);
    targetEl.innerHTML = `<p class="text-sm text-red-500">Failed to load groups.</p>`;
  }
}

// Function to show task assignment modal
// Function to show task assignment modal
function showAssignTaskModal(orgId, groupId, groupName) {
  const existing = document.getElementById("assignTaskModal");
  if (existing) existing.remove();

  const modal = document.createElement("div");
  modal.id = "assignTaskModal";
  modal.className = "fixed inset-0 z-50 flex items-center justify-center bg-black/60 overflow-y-auto py-10";
  modal.innerHTML = `
    <div class="bg-white rounded-xl shadow-xl w-full max-w-3xl p-0 relative animate-fadeIn mx-4">
      <!-- Header Section -->
      <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-indigo-600 to-purple-600 rounded-t-xl">
        <h2 class="text-xl font-bold text-white flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          New Task for <span class="font-bold ml-1">${groupName}</span>
        </h2>
        <button class="text-white hover:text-gray-200 transition-colors focus:outline-none" onclick="document.getElementById('assignTaskModal').remove()">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <!-- Form Section -->
      <form id="assignTaskForm" class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Left Column -->
          <div class="space-y-6">
            <!-- Title -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Task Title <span class="text-red-500">*</span></label>
              <input type="text" name="title" required class="w-full border border-gray-300 rounded-lg p-3 text-sm shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition" placeholder="Enter a descriptive title">
            </div>
            
            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea name="description" rows="4" class="w-full border border-gray-300 rounded-lg p-3 text-sm shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition" placeholder="What needs to be done?"></textarea>
              <p class="mt-1 text-xs text-gray-500">Include all relevant details for better clarity</p>
            </div>
            
            <!-- Project Plan -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Project Plan</label>
              <textarea name="project_plan" rows="3" class="w-full border border-gray-300 rounded-lg p-3 text-sm shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition" placeholder="Strategic approach or methodology"></textarea>
              <p class="mt-1 text-xs text-gray-500">Optional: Add steps or methodology details</p>
            </div>
            
            <!-- Assignee Email -->
            <div class="relative">
              <label class="block text-sm font-medium text-gray-700 mb-1">Assignee Email <span class="text-red-500">*</span></label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <input type="email" name="assigned_email" required class="w-full border border-gray-300 rounded-lg p-3 pl-10 text-sm shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition" placeholder="user@example.com">
              </div>
              <div id="assigneePreview" class="hidden"></div>
              <p class="mt-1 text-xs text-gray-500">Email of the person responsible for this task</p>
            </div>
          </div>
          
          <!-- Right Column -->
          <div class="space-y-6">
            <!-- Priority -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority Level</label>
              <div class="relative">
                <select name="priority" class="w-full border border-gray-300 rounded-lg p-3 text-sm shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition appearance-none pr-10">
                  <option value="low">Low</option>
                  <option value="medium" selected>Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
                <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
              <div class="mt-2 flex space-x-2">
                <span class="px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">Low</span>
                <span class="px-2 py-1 text-xs rounded bg-blue-100 text-blue-700">Medium</span>
                <span class="px-2 py-1 text-xs rounded bg-orange-100 text-orange-700">High</span>
                <span class="px-2 py-1 text-xs rounded bg-red-100 text-red-700">Urgent</span>
              </div>
            </div>
            
            <!-- Status -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Task Status</label>
              <div class="relative">
                <select name="status" class="w-full border border-gray-300 rounded-lg p-3 text-sm shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition appearance-none pr-10">
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                  <option value="overdue">Overdue</option>
                  <option value="pending_approval">Pending Approval</option>
                  <option value="need_changes">Need Changes</option>
                </select>
                <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>
            
            <!-- Dates section -->
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Deadline <span class="text-red-500">*</span></label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <input type="datetime-local" name="deadline" required class="w-full border border-gray-300 rounded-lg p-3 pl-10 text-sm shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition">
                </div>
                <p class="mt-1 text-xs text-gray-500">Final date by which task must be completed</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <input type="datetime-local" name="start_date" class="w-full border border-gray-300 rounded-lg p-3 pl-10 text-sm shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition">
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <input type="datetime-local" name="end_date" class="w-full border border-gray-300 rounded-lg p-3 pl-10 text-sm shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition">
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer with button -->
        <div class="mt-8 border-t border-gray-100 pt-6 flex flex-col sm:flex-row justify-end space-y-4 sm:space-y-0">
          <button type="button" class="px-6 py-3 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition mr-3" onclick="document.getElementById('assignTaskModal').remove()">Cancel</button>
          <button type="submit" class="px-6 py-3 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium hover:from-indigo-700 hover:to-purple-700 transition flex items-center justify-center shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Assign Task
          </button>
        </div>
        
        <div id="assignTaskLoader" class="hidden text-center text-gray-500 mt-4 p-3 bg-gray-50 rounded-lg">
          <div class="flex items-center justify-center">
            <svg class="animate-spin h-5 w-5 mr-3 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Assigning task...</span>
          </div>
        </div>
      </form>
    </div>
  `;

  document.body.appendChild(modal);

  document.getElementById("assignTaskForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const form = e.target;
    const loader = document.getElementById("assignTaskLoader");
    loader.classList.remove("hidden");

    const formData = new FormData(form);
    try {
      const res = await fetch(`/admin_widgets/assign-task-widget/${orgId}/${groupId}/`, {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": getCSRFToken()
        }
      });

      const result = await res.json();
      loader.classList.add("hidden");

      if (result.success) {
        // Success notification
        const notification = document.createElement("div");
        notification.className = "fixed bottom-4 right-4 bg-green-50 border-l-4 border-green-500 p-4 rounded shadow-lg animate-fadeIn z-50 flex items-center";
        notification.innerHTML = `
          <div class="text-green-500 mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-green-800">${result.message}</p>
          </div>
        `;
        document.body.appendChild(notification);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
          notification.classList.add("animate-fadeOut");
          setTimeout(() => notification.remove(), 500);
        }, 3000);
        
        modal.remove();
      } else {
        // Error notification
        const errorMsg = document.createElement("div");
        errorMsg.className = "mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm";
        errorMsg.innerHTML = `
          <div class="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>${result.error || "Failed to assign task."}</span>
          </div>
        `;
        
        // Insert error message before the loader
        loader.parentNode.insertBefore(errorMsg, loader.nextSibling);
        
        // Remove error message after 5 seconds
        setTimeout(() => {
          errorMsg.classList.add("animate-fadeOut");
          setTimeout(() => errorMsg.remove(), 500);
        }, 5000);
      }
    } catch (err) {
      loader.classList.add("hidden");
      console.error(err);
      alert("Something went wrong while assigning task.");
    }
  });
}


// Function to get user by email dynamically
let debounceTimer;

// This will be set up once the modal is created
function setupEmailDebounce() {
  const emailInput = document.querySelector('input[name="assigned_email"]');
  if (!emailInput) return;

  emailInput.addEventListener('input', function () {
    const email = this.value.trim();
    const orgId = window.djangoData.orgId; // Make sure this is correctly injected
    const groupId = CURRENT_GROUP_ID; // Make sure the group ID is dynamically available

    if (debounceTimer) clearTimeout(debounceTimer); // Clear previous timeout
  
    // Only proceed if there's content to search for
    if (email.length < 3) {
      const previewBox = document.getElementById("assigneePreview");
      if (previewBox) previewBox.classList.add("hidden");
      return;
    }
    
    debounceTimer = setTimeout(() => {
      // Show loading indicator
      const previewBox = document.getElementById("assigneePreview");
      if (previewBox) {
        previewBox.classList.remove("hidden");
        previewBox.innerHTML = `
          <div class="p-3 bg-white shadow-lg border rounded-lg mt-1 w-full animate-pulse flex items-center space-x-2">
            <div class="rounded-full bg-gray-200 h-8 w-8"></div>
            <div class="space-y-2 flex-1">
              <div class="h-3 bg-gray-200 rounded w-3/4"></div>
              <div class="h-2 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        `;
      }

      // Fetch user info by email
      fetch(`/admin_widgets/get-user-by-email/${orgId}/${groupId}/?email=${encodeURIComponent(email)}`)
        .then(res => {
          if (!res.ok) {
            throw new Error('Failed to fetch user data');
          }
          return res.json();
        })
        .then(data => {
          const previewBox = document.getElementById("assigneePreview");
          
          if (!previewBox) {
            const newPreviewBox = document.createElement("div");
            newPreviewBox.id = "assigneePreview";
            newPreviewBox.classList.add("absolute", "bg-white", "shadow-lg", "border", "rounded-lg", "w-full", "z-10", "mt-1");
            document.querySelector('input[name="assigned_email"]').parentElement.appendChild(newPreviewBox);
          }

          const previewBoxElement = document.getElementById("assigneePreview");
          previewBoxElement.classList.remove("hidden");

          if (data.success) {
            const user = data.user;

            previewBoxElement.innerHTML = `
              <div class="p-3 bg-white shadow-md border rounded-lg flex items-center space-x-3 hover:bg-gray-50 cursor-pointer">
                <img src="${user.avatar_url || '/static/images/default-avatar.png'}" alt="${user.full_name}" class="w-10 h-10 rounded-full object-cover border-2 border-indigo-100">
                <div>
                  <p class="font-medium text-gray-800">${user.full_name}</p>
                  <p class="text-xs text-gray-500">${user.email}</p>
                </div>
              </div>
            `;
            
            // Click to select user
            previewBoxElement.querySelector('div').addEventListener('click', function() {
              emailInput.value = user.email;
              previewBoxElement.classList.add("hidden");
            });
            
          } else {
            previewBoxElement.innerHTML = `
              <div class="p-3 bg-white shadow-md border rounded-lg">
                <div class="flex items-center space-x-2 text-red-600">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span class="text-sm">${data.error || "User not found in this group"}</span>
                </div>
              </div>
            `;
          }
        })
        .catch(err => {
          console.error('Error fetching user:', err);
          const previewBox = document.getElementById("assigneePreview");
          if (previewBox) {
            previewBox.classList.remove("hidden");
            previewBox.innerHTML = `
              <div class="p-3 bg-white shadow-md border rounded-lg">
                <div class="flex items-center space-x-2 text-red-600">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span class="text-sm">Error fetching user information</span>
                </div>
              </div>
            `;
          }
        });
    }, 400); // 400ms debounce time
  });

  // Hide preview when clicking outside
  document.addEventListener('click', function(e) {
    const previewBox = document.getElementById("assigneePreview");
    const emailInput = document.querySelector('input[name="assigned_email"]');
    
    if (previewBox && emailInput && !emailInput.contains(e.target) && !previewBox.contains(e.target)) {
      previewBox.classList.add("hidden");
    }
  });
}

// Add this at the end of showAssignTaskModal function
document.body.addEventListener('DOMNodeInserted', function(e) {
  if (e.target.id === 'assignTaskModal') {
    setupEmailDebounce();
  }
});


// Function to get CSRF token
function getCSRFToken() {
  const cookies = document.cookie.split(';');
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.startsWith('csrftoken=')) {
      return cookie.substring('csrftoken='.length);
    }
  }
  return '';
}

// Add these styles to your CSS or inline in a style tag
document.head.insertAdjacentHTML('beforeend', `
<style>
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  @keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
  }
  
  .animate-fadeIn {
    animation: fadeIn 0.3s ease-out forwards;
  }
  
  .animate-fadeOut {
    animation: fadeOut 0.3s ease-out forwards;
  }
</style>
`);