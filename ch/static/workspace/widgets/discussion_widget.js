function HandleAndFetchChat(orgId) {
    fetch(`/discussion_widget/fetch-chat-users/${orgId}/`)
      .then(response => response.json())
      .then(data => {
        const container = document.getElementById('discussion-widget');
        container.innerHTML = '';
  
        data.users.forEach(user => {
          const userDiv = document.createElement('div');
          userDiv.className = 'd-flex align-items-center mb-2 chat-user';
          userDiv.setAttribute('data-user-id', user.user_id);
          userDiv.innerHTML = `
          <div class="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors duration-150 cursor-pointer">
            <div class="relative flex-shrink-0">
              <img 
                src="${user.profile_picture || '/static/default-avatar.png'}" 
                class="w-8 h-8 rounded-full object-cover border border-gray-200 dark:border-gray-700"
                alt="${user.full_name}'s avatar"
              >
              ${user.status === 'online' ? 
                '<span class="absolute bottom-0 right-0 block w-2 h-2 bg-green-500 rounded-full ring-1 ring-white dark:ring-gray-800"></span>' : 
                ''
              }
            </div>
            <div class="ml-3 flex flex-col">
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">${user.full_name}</span>
              ${user.title ? 
                `<span class="text-xs text-gray-500 dark:text-gray-400">${user.title}</span>` : 
                ''
              }
            </div>
            ${user.unread_notifications ? 
              `<div class="ml-auto">
                <span class="inline-flex items-center justify-center w-5 h-5 text-xs font-medium text-white bg-indigo-600 rounded-full">
                  ${user.unread_notifications > 9 ? '9+' : user.unread_notifications}
                </span>
              </div>` : 
              ''
            }
          </div>
        `;
          userDiv.addEventListener('click', () => openChatModal(user.user_id, user.full_name, orgId));
          container.appendChild(userDiv);
        });
      })
      .catch(err => console.error("Error loading users:", err));
  }
  
  function openChatModal(userId, userName, orgId) {
    const modal = new bootstrap.Modal(document.getElementById('chatModal'));
    document.getElementById('chatModalLabel').innerText = `Chat with ${userName}`;
    document.getElementById('chatUserId').value = userId;
    document.getElementById('chatOrgId').value = orgId;
    document.getElementById('chatMessages').innerHTML = '';
    modal.show();
  
    fetch(`/discussion_widget/handle-chat/?receiver_id=${userId}&org_id=${orgId}`)
      .then(res => res.json())
      .then(data => {
        const chatBox = document.getElementById('chatMessages');
        data.messages.forEach(msg => {
          const bubble = document.createElement('div');

          // Enhanced chat bubble with Tailwind CSS styling for ClickUp-like UI
bubble.className = msg.sender === CURRENT_USER_ID 
? 'flex flex-col items-end mb-4 max-w-3/4 ml-auto' 
: 'flex flex-col items-start mb-4 max-w-3/4';

// Create avatar element with first letter of sender
const avatar = document.createElement('div');
const senderInitial = (msg.sender.toString()[0] || '?').toUpperCase();
avatar.className = msg.sender === CURRENT_USER_ID
? 'w-8 h-8 rounded-full flex items-center justify-center text-white bg-indigo-600 text-sm font-medium ml-2 order-2'
: 'w-8 h-8 rounded-full flex items-center justify-center text-white bg-gray-500 text-sm font-medium mr-2 order-1';
avatar.textContent = senderInitial;

// Create message content container
const messageContent = document.createElement('div');
messageContent.className = msg.sender === CURRENT_USER_ID
? 'order-1 mr-2 py-2 px-4 bg-indigo-100 rounded-2xl rounded-tr-none shadow-sm text-indigo-900'
: 'order-2 ml-2 py-2 px-4 bg-gray-100 rounded-2xl rounded-tl-none shadow-sm text-gray-900';

// Add message text with proper styling
const messageText = document.createElement('div');
messageText.className = 'text-sm font-normal break-words';
messageText.textContent = msg.text;

// Add timestamp with subtle styling
const timestamp = document.createElement('div');
timestamp.className = 'text-xs text-gray-500 mt-1';
timestamp.textContent = msg.timestamp;

// Append text and timestamp to message content
messageContent.appendChild(messageText);
messageContent.appendChild(timestamp);

// Clear and rebuild the bubble with new structure
bubble.innerHTML = '';
bubble.className += ' flex items-start';
bubble.appendChild(avatar);
bubble.appendChild(messageContent);
          chatBox.appendChild(bubble);
        });
      });
  }
  
  function sendMessage() {
    const userId = document.getElementById('chatUserId').value;
    const orgId = document.getElementById('chatOrgId').value;
    const text = document.getElementById('chatInput').value;
    const file = document.getElementById('chatFile').files[0];
    const code = document.getElementById('chatCode').value;
  
    if (!text.trim() && !file && !code.trim()) return;
  
    const formData = new FormData();
    formData.append('receiver_id', userId);
    formData.append('org_id', orgId);
    formData.append('text', text);
    formData.append('code_snippet', code);
    if (file) formData.append('file', file);
  
    fetch('/discussion_widget/handle-chat/', {
      method: 'POST',
      body: formData,
      headers: { 'X-CSRFToken': getCSRFToken() }
    })
      .then(res => res.json())
      .then(data => {
        const chatBox = document.getElementById('chatMessages');
        const bubble = document.createElement('div');
        bubble.className = 'text-end text-primary';
  
        let content = '<div class="flex flex-col space-y-2">';

        // Message text with proper styling
        if (text) {
          content += `<div class="text-sm text-gray-800 leading-relaxed break-words">${text}</div>`;
        }
        
        // Code snippet with improved styling
        if (code) {
          content += `
            <div class="relative bg-gray-100 rounded-md p-3 border-l-4 border-indigo-500">
              <div class="absolute top-2 right-2 text-xs px-2 py-1 bg-gray-200 rounded text-gray-600 font-medium">CODE</div>
              <pre class="text-xs font-mono text-gray-800 whitespace-pre-wrap overflow-x-auto mt-2 max-h-60 scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100"><code>${code}</code></pre>
            </div>
          `;
        }
        
        // File attachment with icon and better visual
        if (data.file_url) {
          content += `
            <a href="${data.file_url}" target="_blank" class="flex items-center space-x-2 text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 transition duration-200 py-2 px-3 rounded-md w-fit">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
              </svg>
              <span class="text-sm font-medium">Download File</span>
            </a>
          `;
        }
        
        // Timestamp with subtle styling
        content += `<div class="text-xs text-gray-400 mt-1">${data.timestamp}</div>`;
        content += '</div>';
        
        bubble.innerHTML = content;
        chatBox.appendChild(bubble);
  
        document.getElementById('chatInput').value = '';
        document.getElementById('chatCode').value = '';
        document.getElementById('chatFile').value = '';
      });
  }
  
  
  function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  }
  

// save code 
function toggleCodeInput() {
    const codeInput = document.getElementById("chatCode");
    codeInput.style.display = codeInput.style.display === "none" ? "block" : "none";
  }

 
// # Widget 2)Total time traced----------------------------------------------------------------------------------------------------------------
let batteryChart = null;

function FetchTotalTimeBatteryChart() {
  const loading = document.getElementById("timeWidgetLoading");
  const ctx = document.getElementById("batteryChart").getContext("2d");

  // Show loading
  loading.classList.remove("hidden");

  fetch(`/discussion_widget/time-spent-battery-chart/${window.djangoData.orgId}/`)
    .then(response => response.json())
    .then(data => {
      loading.classList.add("hidden");

      if (data.status === 'success') {
        const labels = data.data.map(item => item.user);
        const hours = data.data.map(item => item.time_hours);
        const colors = data.data.map(item => {
          if (item.battery_level >= 75) return 'rgba(34,197,94,0.8)';        // green-500
          if (item.battery_level >= 40) return 'rgba(250,204,21,0.8)';       // yellow-400
          return 'rgba(239,68,68,0.8)';                                      // red-500
        });

        // Destroy old chart instance if exists
        if (batteryChart) {
          batteryChart.destroy();
        }

        batteryChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Time Spent (hours)',
              data: hours,
              backgroundColor: colors,
              borderRadius: 10,
              barThickness: 20
            }]
          },
          options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return `${context.parsed.x.toFixed(2)} hrs`;
                  }
                }
              }
            },
            scales: {
              x: {
                title: {
                  display: true,
                  text: 'Hours Tracked'
                },
                beginAtZero: true
              },
              y: {
                ticks: { font: { weight: 'bold' } }
              }
            }
          }
        });

      } else {
        ctx.canvas.parentElement.innerHTML = `<p class="text-red-600 text-sm">${data.message}</p>`;
      }
    })
    .catch(error => {
      loading.classList.add("hidden");
      console.error("Chart fetch error:", error);
      ctx.canvas.parentElement.innerHTML = `<p class="text-red-600 text-sm">Something went wrong loading the chart.</p>`;
    });
}


// Fetch time spent by groups
let groupTimeChart = null;

function FetchGroupTimeChart(orgId) {
  const loader = document.getElementById("groupChartLoading");
  const ctx = document.getElementById("groupTimeChart").getContext("2d");
  
  // Reset canvas if it was previously used
  if (groupTimeChart) {
    groupTimeChart.destroy();
    groupTimeChart = null;
  }
  
  // Style the chart container with Tailwind
  const chartContainer = document.getElementById("groupTimeChart").parentElement;
  chartContainer.classList.add("bg-white", "rounded-lg", "shadow-md", "p-6", "mb-8");
  
  // Add title with SaaS styling
  const chartTitle = document.createElement("div");
  chartTitle.innerHTML = `
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-semibold text-gray-800">Group Time Analysis</h3>
        <p class="text-sm text-gray-500">Hours tracked by team group</p>
      </div>
      <div class="flex items-center space-x-2">
        <div class="bg-gray-100 rounded-md p-1">
          <select id="groupTimeRange" class="bg-transparent text-sm text-gray-600 font-medium px-2 py-1 border-none focus:ring-0 cursor-pointer">
            <option value="week">This Week</option>
            <option value="month" selected>This Month</option>
            <option value="quarter">This Quarter</option>
          </select>
        </div>
        <button class="text-gray-400 hover:text-indigo-600 transition-colors" title="Refresh data">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>
  `;
  chartContainer.prepend(chartTitle);
  
  // Create loading indicator with Tailwind
  loader.innerHTML = `
    <div class="flex justify-center items-center py-12">
      <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
  `;
  loader.classList.remove("d-none");
  loader.classList.add("hidden");
  
  // Create canvas wrapper with appropriate height
  const canvasWrapper = document.createElement("div");
  canvasWrapper.classList.add("h-64", "mt-4");
  canvasWrapper.appendChild(document.getElementById("groupTimeChart"));
  chartContainer.appendChild(canvasWrapper);
  
  loader.classList.remove("hidden");
  
  fetch(`/discussion_widget/time-spent-by-group/${orgId}/`)
    .then(res => res.json())
    .then(data => {
      loader.classList.add("hidden");
      
      if (data.status === "success") {
        const labels = data.data.map(g => g.group);
        const values = data.data.map(g => g.time_hours);
        
        // Custom font settings for Chart.js
        Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";
        Chart.defaults.font.size = 12;
        
        // Create custom gradients
        const ctx = document.getElementById("groupTimeChart").getContext("2d");
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(99, 102, 241, 0.8)');    // indigo-500
        gradient.addColorStop(1, 'rgba(129, 140, 248, 0.6)');   // indigo-400
        
        groupTimeChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Total Hours',
              data: values,
              backgroundColor: gradient,
              borderColor: 'rgba(99, 102, 241, 1)',  // indigo-500
              borderWidth: 1,
              borderRadius: 6,
              barThickness: 28,
              maxBarThickness: 35
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
              padding: {
                top: 15,
                right: 25,
                bottom: 15,
                left: 15
              }
            },
            plugins: {
              legend: { display: false },
              tooltip: {
                backgroundColor: 'rgba(17, 24, 39, 0.9)',
                padding: 12,
                titleFont: {
                  size: 13,
                  weight: 'bold'
                },
                bodyFont: {
                  size: 12
                },
                displayColors: false,
                callbacks: {
                  title: function(tooltipItems) {
                    return tooltipItems[0].label;
                  },
                  label: function(context) {
                    const hours = context.parsed.y;
                    return `${hours} ${hours === 1 ? 'hour' : 'hours'}`;
                  }
                }
              }
            },
            scales: {
              x: {
                grid: {
                  display: false,
                  drawBorder: false
                },
                ticks: {
                  color: '#4B5563', // text-gray-600
                  font: {
                    weight: '500'
                  },
                  padding: 8
                }
              },
              y: {
                beginAtZero: true,
                grid: {
                  color: 'rgba(243, 244, 246, 1)', // gray-100
                  drawBorder: false
                },
                ticks: {
                  color: '#6B7280', // text-gray-500
                  padding: 8,
                  callback: function(val) {
                    return val + " hrs";
                  }
                }
              }
            }
          }
        });
        
        // Add footer stats
        const chartFooter = document.createElement("div");
        chartFooter.classList.add("flex", "justify-between", "items-center", "mt-6", "pt-4", "border-t", "border-gray-100", "text-sm");
        
        // Calculate stats
        const totalHours = values.reduce((sum, current) => sum + current, 0);
        const maxGroupHours = Math.max(...values);
        const maxGroupName = labels[values.indexOf(maxGroupHours)];
        
        chartFooter.innerHTML = `
          <div class="flex space-x-6">
            <div>
              <p class="text-gray-500 mb-1">Total Hours</p>
              <p class="text-lg font-semibold text-gray-800">${totalHours}</p>
            </div>
            <div>
              <p class="text-gray-500 mb-1">Top Group</p>
              <p class="text-lg font-semibold text-gray-800">${maxGroupName}</p>
            </div>
          </div>
          <div>
            <button class="text-sm text-indigo-600 hover:text-indigo-800 font-medium transition-colors flex items-center">
              <span>Full Report</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        `;
        chartContainer.appendChild(chartFooter);
        
      } else {
        const errorMessage = document.createElement("div");
        errorMessage.classList.add("bg-red-50", "text-red-600", "p-4", "rounded-md", "flex", "items-center", "justify-center", "my-4");
        errorMessage.innerHTML = `
          <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>No data available for the selected time period.</span>
        `;
        ctx.canvas.parentElement.appendChild(errorMessage);
      }
    })
    .catch(err => {
      loader.classList.add("hidden");
      console.error("Error fetching group time chart:", err);
      
      const errorMessage = document.createElement("div");
      errorMessage.classList.add("bg-red-50", "text-red-600", "p-4", "rounded-md", "flex", "items-center", "justify-center", "my-4");
      errorMessage.innerHTML = `
        <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Something went wrong loading the chart. Please try again.</span>
        <button class="ml-2 text-indigo-600 hover:text-indigo-800 font-medium text-sm" onclick="FetchGroupTimeChart('${orgId}')">
          Retry
        </button>
      `;
      ctx.canvas.parentElement.appendChild(errorMessage);
    });
}


// # Widget 4) Total tasks by assignee-------------------------------------------------------------------------------------------------------------------------------------------
function TasksByAssigneePieChart(orgId) {
  // Original functionality elements
  const loading = document.getElementById("taskStatusPieLoading");
  const canvas = document.getElementById("taskStatusPieChart");
  const ctx = canvas.getContext("2d");
  
  // Clear any previous chart instance
  if (window.taskStatusPieInstance) {
    window.taskStatusPieInstance.destroy();
  }
  
  // Wrap canvas in SaaS-style container if not already wrapped
  let container = document.getElementById("task-chart-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "task-chart-container";
    canvas.parentNode.insertBefore(container, canvas);
    container.appendChild(canvas);
    
    // Create header section
    const header = document.createElement("div");
    header.id = "task-chart-header";
    container.insertBefore(header, canvas);
    
    // Create card-style container for the chart
    const chartCard = document.createElement("div");
    chartCard.id = "task-chart-card";
    chartCard.appendChild(canvas);
    container.appendChild(chartCard);
    
    // Create legend container that will be populated after chart renders
    const legendContainer = document.createElement("div");
    legendContainer.id = "task-chart-legend";
    container.appendChild(legendContainer);
  }
  
  // Apply ClickUp-inspired styling to container and components
  container.className = "bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden w-full max-w-3xl mx-auto";
  document.getElementById("task-chart-header").className = "px-6 py-4 border-b border-gray-200 flex justify-between items-center";
  document.getElementById("task-chart-card").className = "px-6 py-6 relative";
  document.getElementById("task-chart-legend").className = "px-6 pt-2 pb-6";
  
  // Style the canvas itself
  canvas.className = "h-64 w-full";
  
  // Create enhanced loading indicator
  loading.className = "absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-10";
  loading.innerHTML = `
    <div class="flex flex-col items-center">
      <svg class="animate-spin w-8 h-8 text-purple-600 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="text-sm font-medium text-gray-700">Loading task data...</p>
    </div>
  `;
  
  // Add ClickUp-inspired header content
  document.getElementById("task-chart-header").innerHTML = `
    <div>
      <h3 class="text-lg font-semibold text-gray-800">Tasks by Status</h3>
      <p class="text-xs text-gray-500 mt-1">Distribution of tasks across different status categories</p>
    </div>
    <div class="flex items-center space-x-2">
        <button onclick="TasksByAssigneePieChart(window.djangoData.orgId)" title="Refresh"
        class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-500 hover:text-indigo-600 transition" fill="none"
          viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M4 4v5h.582m15.406 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m-15.406-2a8.001 8.001 0 0015.406 2m0 0H15" />
        </svg>
      </button>

          <button onclick="openFullScreenWidget('tasks-by-assignee-widget')" title="Fullscreen"
        class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
        <svg class="w-5 h-5 text-gray-400 hover:text-indigo-600 transition" fill="none" stroke="currentColor"
          viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
      </button>


      <div class="relative">
        <select id="chart-type-selector" class="appearance-none bg-gray-100 text-gray-700 text-sm font-medium py-1 pl-3 pr-8 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 cursor-pointer">
          <option value="pie">Pie Chart</option>
          <option value="doughnut">Doughnut Chart</option>
        </select>
        <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </div>
      </div>
    </div>
  `;
  
  // Show loading indicator
  loading.classList.remove("d-none");
  
  // Original fetch functionality maintained
  fetch(`/discussion_widget/tasks-by-assignee/${window.djangoData.orgId}/`)
    .then(res => res.json())
    .then(data => {
      loading.classList.add("d-none");
      
      if (data.status === 'success' && data.data.length > 0) {
        // Data processing logic is unchanged
        const statusCounts = {};
        data.data.forEach(task => {
          const status = task.status;
          statusCounts[status] = (statusCounts[status] || 0) + 1;
        });
        
        const labels = Object.keys(statusCounts);
        const values = Object.values(statusCounts);
        const totalTasks = values.reduce((sum, count) => sum + count, 0);
        
        // Update header with task count
        const headerTitle = document.querySelector("#task-chart-header h3");
        headerTitle.textContent = `Tasks by Status (${totalTasks})`;
        
        // ClickUp-inspired color palette - vibrant, distinct but harmonious
        const colors = [
          '#7b68ee', // Medium slate blue (Primary color)
          '#4cc9f0', // Cyan
          '#06d6a0', // Green
          '#ffbe0b', // Yellow
          '#ff5400', // Orange
          '#e63946', // Red
          '#8338ec', // Purple
          '#3a86ff'  // Blue
        ];
        
        // Create chart with enhanced styling
        const chartConfig = {
          type: 'pie',
          data: {
            labels: labels,
            datasets: [{
              data: values,
              backgroundColor: colors.slice(0, labels.length),
              borderColor: '#ffffff',
              borderWidth: 2,
              hoverOffset: 10
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
              padding: 20
            },
            plugins: {
              legend: {
                display: false // We'll create a custom legend below
              },
              tooltip: {
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                titleColor: '#111827',
                titleFont: {
                  family: "'Inter', 'Segoe UI', sans-serif",
                  size: 14,
                  weight: 'bold'
                },
                bodyColor: '#4b5563',
                bodyFont: {
                  family: "'Inter', 'Segoe UI', sans-serif",
                  size: 13
                },
                padding: 12,
                boxPadding: 6,
                borderColor: '#e5e7eb',
                borderWidth: 1,
                callbacks: {
                  // Enhanced tooltip showing percentage
                  label: function(context) {
                    const value = context.parsed;
                    const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                    const percentage = Math.round((value / total) * 100);
                    return `${value} tasks (${percentage}%)`;
                  }
                }
              }
            },
            elements: {
              arc: {
                borderWidth: 1
              }
            },
            animation: {
              animateScale: true,
              animateRotate: true,
              duration: 800,
              easing: 'easeOutQuart'
            }
          }
        };
        
        window.taskStatusPieInstance = new Chart(ctx, chartConfig);
        
        // Create ClickUp-style custom legend
        const legendContainer = document.getElementById("task-chart-legend");
        let legendHTML = '<div class="grid grid-cols-2 md:grid-cols-3 gap-4 mt-2">';
        
        labels.forEach((label, index) => {
          const count = values[index];
          const percentage = Math.round((count / totalTasks) * 100);
          
          legendHTML += `
            <div class="flex items-center group">
              <div class="w-3 h-3 rounded-sm mr-2" style="background-color: ${colors[index]}"></div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <p class="text-sm font-medium text-gray-700 truncate group-hover:text-gray-900">${label}</p>
                  <p class="ml-2 text-sm font-medium text-gray-900">${count}</p>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                  <div class="h-1.5 rounded-full" style="width: ${percentage}%; background-color: ${colors[index]}"></div>
                </div>
              </div>
            </div>
          `;
        });
        
        legendHTML += '</div>';
        legendContainer.innerHTML = legendHTML;
        
        // Add chart type selector functionality
        const chartTypeSelector = document.getElementById("chart-type-selector");
        chartTypeSelector.addEventListener("change", function() {
          if (window.taskStatusPieInstance) {
            window.taskStatusPieInstance.destroy();
          }
          
          chartConfig.type = this.value;
          if (this.value === 'doughnut') {
            chartConfig.options.cutout = '60%';
          } else {
            delete chartConfig.options.cutout;
          }
          
          window.taskStatusPieInstance = new Chart(ctx, chartConfig);
        });
        
      } else {
        // Empty state with ClickUp styling
        document.getElementById("task-chart-card").innerHTML = `
          <div class="flex flex-col items-center justify-center py-12 px-4 text-center">
            <svg class="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            </svg>
            <h4 class="text-lg font-medium text-gray-700 mb-1">No tasks found</h4>
            <p class="text-sm text-gray-500 mb-4 max-w-sm">There are currently no assigned tasks to display in this chart</p>
            <button class="inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              Create Task
            </button>
          </div>
        `;
        document.getElementById("task-chart-legend").innerHTML = '';
      }
    })
    .catch(err => {
      loading.classList.add("d-none");
      console.error("Error loading pie chart:", err);
      
      // Error state with ClickUp styling
      document.getElementById("task-chart-card").innerHTML = `
        <div class="flex flex-col items-center justify-center py-10 px-4 text-center">
          <div class="rounded-full bg-red-100 p-3 mb-4">
            <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <h4 class="text-lg font-medium text-gray-800 mb-1">Failed to load data</h4>
          <p class="text-sm text-gray-500 mb-4 max-w-sm">There was a problem fetching task statistics</p>
          <button onclick="TasksByAssigneePieChart()" class="inline-flex items-center px-4 py-2 border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 text-sm font-medium rounded-md shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            Try Again
          </button>
        </div>
      `;
      document.getElementById("task-chart-legend").innerHTML = '';
    });
}