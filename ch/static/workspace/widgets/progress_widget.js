function fetchAndRenderProgress(orgId) {
    const widget = document.getElementById('progress-widget');
    if (!widget) return;
    
    // Add ClickUp-inspired styling to the container
    widget.classList.add('bg-white', 'rounded-lg', 'shadow-md', 'border', 'border-gray-200', 'p-4');
    
    // Create header if it doesn't exist
    let header = widget.querySelector('.progress-header');
    if (!header) {
      header = document.createElement('div');
      header.className = 'progress-header flex justify-between items-center mb-4 pb-3 border-b border-gray-200';
      header.innerHTML = `
        <h3 class="text-base font-semibold text-indigo-700">Tasks Portfolio Accross All Groups</h3>
        <span class="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded-full">Active</span>
      `;
      widget.prepend(header);
    }
    
    // Ensure the task container has max height and scrolling
    let container = widget.querySelector(".task-progress-container");
    if (!container) {
      container = document.createElement('div');
      container.className = "task-progress-container";
      widget.appendChild(container);
    }
    container.classList.add('max-h-80', 'overflow-y-auto', 'pr-1', 'scrollbar-thin', 'scrollbar-thumb-gray-300', 'scrollbar-track-gray-100');
    
    // Add custom scrollbar styling
    const style = document.createElement('style');
    style.textContent = `
      .scrollbar-thin::-webkit-scrollbar {
        width: 6px;
      }
      .scrollbar-thumb-gray-300::-webkit-scrollbar-thumb {
        background-color: #d1d5db;
        border-radius: 3px;
      }
      .scrollbar-track-gray-100::-webkit-scrollbar-track {
        background-color: #f3f4f6;
      }
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .tooltip-box {
        animation: fadeIn 0.2s ease-in-out;
      }
    `;
    document.head.appendChild(style);
  
    // Show loading state
    container.innerHTML = `
      <div class="flex justify-center items-center py-6">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500"></div>
        <span class="ml-3 text-sm text-gray-500">Loading tasks...</span>
      </div>
    `;
  
    fetch(`/progress/user-task-progress-widget/${orgId}/`)
      .then(response => response.json())
      .then(data => {
        container.innerHTML = "";
        
        if (data.tasks.length === 0) {
          container.innerHTML = `
            <div class="flex flex-col items-center justify-center py-8 text-center">
              <svg class="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
              </svg>
              <p class='text-sm font-medium text-gray-400'>No tasks assigned</p>
              <p class='text-xs text-gray-400 mt-1'>Tasks assigned to you will appear here</p>
            </div>
          `;
          return;
        }
        
        data.tasks.forEach(task => {
          const taskBlock = document.createElement("div");
          taskBlock.className = "mb-4 p-3 bg-white border border-gray-100 rounded-lg hover:shadow-sm transition-all duration-200 relative";
          
          // Status indicator
          const statusIndicator = document.createElement("div");
          const statusColor = task.progress === 100 ? 'bg-green-500' : task.progress > 75 ? 'bg-indigo-500' : task.progress > 25 ? 'bg-yellow-500' : 'bg-red-500';
          statusIndicator.className = `absolute top-3 left-0 w-1 h-12 ${statusColor} rounded-r`;
          taskBlock.appendChild(statusIndicator);
          
          // Title with icon
          const titleDiv = document.createElement("div");
          titleDiv.className = "text-sm font-medium text-gray-800 cursor-pointer tooltip-anchor flex items-center pl-3";
          
          const titleIcon = document.createElement("span");
          titleIcon.className = "mr-2 text-indigo-500";
          titleIcon.innerHTML = `
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            </svg>
          `;
          
          const titleText = document.createElement("span");
          titleText.textContent = task.title;
          titleText.className = "truncate";
          
          titleDiv.appendChild(titleIcon);
          titleDiv.appendChild(titleText);
          
          // Group with icon
          const groupDiv = document.createElement("div");
          groupDiv.className = "text-xs text-gray-500 mb-3 mt-1 pl-9";
          groupDiv.innerHTML = `
            <span class="inline-flex items-center">
              <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
              ${task.group__name}
            </span>
          `;
          
          // Progress bar
          const progressBarContainer = document.createElement("div");
          progressBarContainer.className = "w-full bg-gray-100 rounded-full h-2 mt-2";
          
          const progressBar = document.createElement("div");
          const barColor = task.progress === 100 ? 'bg-green-500' : task.progress > 75 ? 'bg-indigo-500' : task.progress > 25 ? 'bg-yellow-500' : 'bg-red-500';
          progressBar.className = `${barColor} h-2 rounded-full transition-all duration-700 ease-out`;
          progressBar.style.width = "0%"; // Start at 0 for animation
          progressBarContainer.appendChild(progressBar);
          
          // Progress percentage
          const percentContainer = document.createElement("div");
          percentContainer.className = "flex justify-between items-center text-xs mt-1";
          
          const percentText = document.createElement("div");
          percentText.className = "text-gray-500";
          percentText.textContent = `${task.progress}% Complete`;
          
          const progressStatus = document.createElement("div");
          progressStatus.className = task.progress === 100 ? "text-green-500" : "text-indigo-500";
          progressStatus.textContent = task.progress === 100 ? "Complete" : "In Progress";
          
          percentContainer.appendChild(percentText);
          percentContainer.appendChild(progressStatus);
          
          // Tooltip logic - attach inside closure
          titleDiv.addEventListener("mouseenter", () => {
            fetch(`/progress/get-task-progress-details/${orgId}/${task.id}/`)
              .then(res => res.json())
              .then(data => {
                const tooltip = document.createElement("div");
                tooltip.className = "absolute z-50 bg-white border border-gray-200 text-xs p-0 rounded-lg shadow-lg tooltip-box w-64";
                
                const rect = titleDiv.getBoundingClientRect();
                tooltip.style.top = `${rect.top + window.scrollY + 30}px`;
                tooltip.style.left = `${rect.left + window.scrollX}px`;
                
                tooltip.innerHTML = `
                  <div class="p-3 border-b border-gray-100 bg-gray-50 rounded-t-lg">
                    <div class="font-medium text-gray-800 mb-1">${task.title}</div>
                    <div class="text-gray-500 text-xs">${task.group__name}</div>
                  </div>
                  <div class="p-3">
                    <div class="grid grid-cols-2 gap-2">
                      <div class="flex items-center">
                        <svg class="w-3 h-3 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                        </svg>
                        <span class="text-gray-600">${data.assigned_by}</span>
                      </div>
                      <div class="flex items-center">
                        <svg class="w-3 h-3 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        <span class="text-gray-600">${data.deadline}</span>
                      </div>
                      <div class="flex items-center">
                        <svg class="w-3 h-3 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <span class="${data.remaining_days < 2 ? 'text-red-500 font-medium' : 'text-gray-600'}">${data.remaining_days} days left</span>
                      </div>
                      <div class="flex items-center">
                        <svg class="w-3 h-3 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                        </svg>
                        <span class="text-gray-600">${data.subtasks.completed} / ${data.subtasks.total} subtasks</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-gray-50 p-2 text-center rounded-b-lg border-t border-gray-100">
                    <span class="text-xs text-indigo-600 font-medium">Click to view details</span>
                  </div>
                `;
                
                document.body.appendChild(tooltip);
                titleDiv._tooltip = tooltip;
              });
          });
          
          titleDiv.addEventListener("mouseleave", () => {
            if (titleDiv._tooltip) {
              titleDiv._tooltip.remove();
              titleDiv._tooltip = null;
            }
          });
          
          // Append all
          taskBlock.appendChild(titleDiv);
          taskBlock.appendChild(groupDiv);
          taskBlock.appendChild(progressBarContainer);
          taskBlock.appendChild(percentContainer);
          container.appendChild(taskBlock);
          
          // Animate the progress bar
          setTimeout(() => {
            progressBar.style.width = `${task.progress}%`;
          }, 100);
        });
      })
      .catch(error => {
        console.error("Error fetching progress:", error);
        container.innerHTML = `
          <div class="text-center py-6">
            <svg class="w-12 h-12 text-red-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="text-sm font-medium text-gray-600">Error loading tasks</p>
            <p class="text-xs text-gray-500 mt-1">Please try again later</p>
          </div>
        `;
      });
  }


// Widget 2 -------------------------------------Overdue tasks ---------------------------------------------------------------
function fetchAndRenderOverdueTasks(orgId) {
  const widget = document.getElementById('overdue-tasks-widget');
  if (!widget) return;
  
  // Add ClickUp-inspired styling to the container
  widget.classList.add('bg-white', 'rounded-lg', 'shadow-md', 'border', 'border-gray-200', 'p-4');
  
  // Create header if it doesn't exist
  let header = widget.querySelector('.overdue-header');
  if (!header) {
    header = document.createElement('div');
    header.className = 'overdue-header flex justify-between items-center mb-4 pb-3 border-b border-gray-200';
    header.innerHTML = `
      <div class="flex items-center">
        <svg class="w-4 h-4 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <h3 class="text-base font-semibold text-red-700">Overdue Tasks</h3>
      </div>
      <span class="text-xs font-medium text-red-600 bg-red-50 px-2 py-1 rounded-full flex items-center">
        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        Attention Required
      </span>
    `;
    widget.prepend(header);
  }
  
  // Ensure the task container has max height and scrolling
  let container = widget.querySelector(".overdue-task-container");
  if (!container) {
    container = document.createElement('div');
    container.className = "overdue-task-container";
    widget.appendChild(container);
  }
  container.classList.add('max-h-80', 'overflow-y-auto', 'pr-1', 'scrollbar-thin', 'scrollbar-thumb-gray-300', 'scrollbar-track-gray-100');
  
  // Add custom scrollbar styling if not already added
  if (!document.getElementById('scrollbar-style')) {
    const style = document.createElement('style');
    style.id = 'scrollbar-style';
    style.textContent = `
      .scrollbar-thin::-webkit-scrollbar {
        width: 6px;
      }
      .scrollbar-thumb-gray-300::-webkit-scrollbar-thumb {
        background-color: #d1d5db;
        border-radius: 3px;
      }
      .scrollbar-track-gray-100::-webkit-scrollbar-track {
        background-color: #f3f4f6;
      }
      .card-appear {
        animation: cardAppear 0.3s ease-out forwards;
      }
      @keyframes cardAppear {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .overdue-pulse {
        animation: pulse 2s infinite;
      }
      @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.2); }
        70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
      }
    `;
    document.head.appendChild(style);
  }

  // Show loading state
  container.innerHTML = `
    <div class="flex justify-center items-center py-6">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-red-500"></div>
      <span class="ml-3 text-sm text-gray-500">Loading overdue tasks...</span>
    </div>
  `;

  fetch(`/progress/get-overdue-tasks/${orgId}/`)
    .then(response => response.json())
    .then(data => {
      container.innerHTML = "";
      
      if (!data.overdue_tasks || data.overdue_tasks.length === 0) {
        container.innerHTML = `
          <div class="flex flex-col items-center justify-center py-8 text-center">
            <div class="bg-green-100 rounded-full p-3 mb-3">
              <svg class="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <p class='text-sm font-medium text-gray-700'>No overdue tasks 🎉</p>
            <p class='text-xs text-gray-400 mt-1'>You're all caught up!</p>
          </div>
        `;
        return;
      }
      
      // Update header count
      const countBadge = widget.querySelector('.overdue-count');
      if (!countBadge) {
        const headerTitle = widget.querySelector('.overdue-header h3');
        if (headerTitle) {
          const badge = document.createElement('span');
          badge.className = 'overdue-count ml-2 bg-red-100 text-red-700 text-xs font-medium px-2 py-0.5 rounded-full';
          badge.textContent = data.overdue_tasks.length;
          headerTitle.appendChild(badge);
        }
      } else {
        countBadge.textContent = data.overdue_tasks.length;
      }
      
      // Sort tasks by most overdue first
      data.overdue_tasks.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
      
      data.overdue_tasks.forEach((task, index) => {
        const checkUrl = `http://127.0.0.1:8000/tasks/task_detail/${orgId}/${task.group__id}/${task.id}/`;
        
        // Calculate days overdue
        const deadlineDate = new Date(task.deadline);
        const today = new Date();
        const daysOverdue = Math.floor((today - deadlineDate) / (1000 * 60 * 60 * 24));
        
        const taskDiv = document.createElement("div");
        taskDiv.className = `
          relative mb-3 rounded-lg border border-red-200 bg-red-50 p-3
          hover:shadow-md group transition-all duration-200 card-appear
          ${daysOverdue > 3 ? 'overdue-pulse' : ''}
        `;
        
        // Set animation delay for staggered appearance
        taskDiv.style.animationDelay = `${index * 0.1}s`;
        
        // Left border indicator
        const urgencyLevel = daysOverdue > 7 ? 'bg-red-600' : daysOverdue > 3 ? 'bg-red-500' : 'bg-red-400';
        const indicator = document.createElement('div');
        indicator.className = `absolute top-0 left-0 w-1 h-full ${urgencyLevel} rounded-l-lg`;
        taskDiv.appendChild(indicator);
        
        // Task content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'pl-3';
        
        const formattedDate = new Intl.DateTimeFormat('en-US', {
          month: 'short',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        }).format(deadlineDate);
        
        contentDiv.innerHTML = `
          <div class="flex items-center">
            <svg class="w-3 h-3 text-red-500 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div class="text-sm font-medium text-gray-800">${task.title}</div>
          </div>
          
          <div class="flex items-center text-xs text-gray-500 mt-1">
            <svg class="w-3 h-3 text-gray-400 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
            <span>${task.group__name}</span>
          </div>
          
          <div class="flex justify-between items-center mt-2">
            <div class="flex items-center text-xs font-medium ${daysOverdue > 7 ? 'text-red-600' : 'text-red-500'}">
              <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>Due ${formattedDate} (${daysOverdue} ${daysOverdue === 1 ? 'day' : 'days'} overdue)</span>
            </div>
            
            <div class="hidden group-hover:block">
              <a href="${checkUrl}" 
                class="inline-flex items-center text-xs px-2 py-1 rounded bg-indigo-600 text-white hover:bg-indigo-700 transition-colors duration-200">
                <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                </svg>
                View
              </a>
            </div>
          </div>
        `;
        
        taskDiv.appendChild(contentDiv);
        container.appendChild(taskDiv);
      });
      
      // Add urgency summary at the bottom
      const criticalCount = data.overdue_tasks.filter(t => new Date() - new Date(t.deadline) > 7 * 24 * 60 * 60 * 1000).length;
      const highCount = data.overdue_tasks.filter(t => {
        const diff = new Date() - new Date(t.deadline);
        return diff <= 7 * 24 * 60 * 60 * 1000 && diff > 3 * 24 * 60 * 60 * 1000;
      }).length;
      const normalCount = data.overdue_tasks.length - criticalCount - highCount;
      
      const summaryDiv = document.createElement('div');
      summaryDiv.className = 'mt-4 pt-3 border-t border-gray-200 flex justify-between items-center text-xs text-gray-500';
      summaryDiv.innerHTML = `
        <div class="flex space-x-3">
          ${criticalCount > 0 ? `<span class="inline-flex items-center"><span class="w-2 h-2 rounded-full bg-red-600 mr-1"></span> ${criticalCount} critical</span>` : ''}
          ${highCount > 0 ? `<span class="inline-flex items-center"><span class="w-2 h-2 rounded-full bg-red-500 mr-1"></span> ${highCount} high</span>` : ''}
          ${normalCount > 0 ? `<span class="inline-flex items-center"><span class="w-2 h-2 rounded-full bg-red-400 mr-1"></span> ${normalCount} normal</span>` : ''}
        </div>
        <a href="#" class="text-indigo-600 hover:text-indigo-800 font-medium">View All</a>
      `;
      container.appendChild(summaryDiv);
    })
    .catch(error => {
      console.error("Error fetching overdue tasks:", error);
      container.innerHTML = `
        <div class="text-center py-6">
          <svg class="w-12 h-12 text-red-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p class="text-sm font-medium text-gray-600">Error loading overdue tasks</p>
          <p class="text-xs text-gray-500 mt-1">Please try again later</p>
        </div>
      `;
    });
}



// Widget 3) Due Soon Tasks in next 14 days ---------------------------------------------------------------------------------------------------------
function fetchAndRenderDueSoonTasks(orgId) {
  const widget = document.getElementById('due-soon-tasks-widget');
  if (!widget) return;
  
  // Add ClickUp-inspired styling to the container
  widget.classList.add('bg-white', 'rounded-lg', 'shadow-md', 'border', 'border-gray-200', 'p-4');
  
  // Create header if it doesn't exist
  let header = widget.querySelector('.due-soon-header');
  if (!header) {
    header = document.createElement('div');
    header.className = 'due-soon-header flex justify-between items-center mb-4 pb-3 border-b border-gray-200';
    header.innerHTML = `
      <div class="flex items-center">
        <svg class="w-4 h-4 text-yellow-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <h3 class="text-base font-semibold text-yellow-700">Due Soon</h3>
      </div>
      <span class="text-xs font-medium text-yellow-600 bg-yellow-50 px-2 py-1 rounded-full flex items-center">
        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        Next 14 Days
      </span>
    `;
    widget.prepend(header);
  }
  
  // Ensure the task container has max height and scrolling
  let container = widget.querySelector(".due-soon-task-container");
  if (!container) {
    container = document.createElement('div');
    container.className = "due-soon-task-container";
    widget.appendChild(container);
  }
  container.classList.add('max-h-80', 'overflow-y-auto', 'pr-1', 'scrollbar-thin', 'scrollbar-thumb-gray-300', 'scrollbar-track-gray-100');
  
  // Add custom scrollbar styling if not already added
  if (!document.getElementById('due-soon-style')) {
    const style = document.createElement('style');
    style.id = 'due-soon-style';
    style.textContent = `
      .due-soon-fade-in {
        animation: dueSoonFadeIn 0.3s ease-out forwards;
        opacity: 0;
      }
      @keyframes dueSoonFadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .due-soon-highlight {
        animation: dueSoonHighlight 2s infinite;
      }
      @keyframes dueSoonHighlight {
        0% { background-color: rgba(254, 249, 195, 0.5); }
        50% { background-color: rgba(254, 240, 138, 0.3); }
        100% { background-color: rgba(254, 249, 195, 0.5); }
      }
    `;
    document.head.appendChild(style);
  }

  // Show loading state
  container.innerHTML = `
    <div class="flex justify-center items-center py-6">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-yellow-500"></div>
      <span class="ml-3 text-sm text-gray-500">Loading upcoming tasks...</span>
    </div>
  `;

  fetch(`/progress/get-due-soon-tasks/${orgId}/`)
    .then(response => response.json())
    .then(data => {
      container.innerHTML = "";
      
      if (!data.due_soon_tasks || data.due_soon_tasks.length === 0) {
        container.innerHTML = `
          <div class="flex flex-col items-center justify-center py-8 text-center">
            <div class="bg-green-100 rounded-full p-3 mb-3">
              <svg class="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <p class='text-sm font-medium text-gray-700'>No tasks due in the next 14 days 🎉</p>
            <p class='text-xs text-gray-400 mt-1'>You're all caught up!</p>
          </div>
        `;
        return;
      }
      
      // Update header count
      const countBadge = widget.querySelector('.due-soon-count');
      if (!countBadge) {
        const headerTitle = widget.querySelector('.due-soon-header h3');
        if (headerTitle) {
          const badge = document.createElement('span');
          badge.className = 'due-soon-count ml-2 bg-yellow-100 text-yellow-700 text-xs font-medium px-2 py-0.5 rounded-full';
          badge.textContent = data.due_soon_tasks.length;
          headerTitle.appendChild(badge);
        }
      } else {
        countBadge.textContent = data.due_soon_tasks.length;
      }
      
      // Sort tasks by soonest deadline first
      data.due_soon_tasks.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
      
      // Group tasks by days remaining
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      const tasksByDueDate = {
        today: [],
        tomorrow: [],
        thisWeek: [], // 2-7 days
        nextWeek: []  // 8-14 days
      };
      
      data.due_soon_tasks.forEach(task => {
        const deadlineDate = new Date(task.deadline);
        deadlineDate.setHours(0, 0, 0, 0);
        
        const timeDiff = deadlineDate - today;
        const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
        
        if (daysDiff === 0) {
          tasksByDueDate.today.push(task);
        } else if (daysDiff === 1) {
          tasksByDueDate.tomorrow.push(task);
        } else if (daysDiff <= 7) {
          tasksByDueDate.thisWeek.push(task);
        } else {
          tasksByDueDate.nextWeek.push(task);
        }
      });
      
      // Function to render section if it has tasks
      const renderSection = (title, tasks, highlight = false) => {
        if (tasks.length === 0) return '';
        
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'mb-4';
        
        const titleDiv = document.createElement('div');
        titleDiv.className = 'flex items-center mb-2';
        titleDiv.innerHTML = `
          <div class="text-xs font-semibold text-gray-500 uppercase flex items-center">
            ${title}
            <span class="ml-2 bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded text-xs font-medium">${tasks.length}</span>
          </div>
        `;
        
        sectionDiv.appendChild(titleDiv);
        
        tasks.forEach((task, index) => {
          const taskDiv = renderTask(task, index, highlight);
          sectionDiv.appendChild(taskDiv);
        });
        
        container.appendChild(sectionDiv);
      };
      
      // Function to render individual task
      const renderTask = (task, index, highlight) => {
        const deadlineDate = new Date(task.deadline);
        const now = new Date();
        const hoursLeft = Math.round((deadlineDate - now) / (1000 * 60 * 60));
        
        const taskDiv = document.createElement("div");
        taskDiv.className = `
          mb-3 rounded-lg border border-yellow-200 bg-yellow-50 
          group relative due-soon-fade-in
          ${highlight && hoursLeft < 24 ? 'due-soon-highlight' : ''}
        `;
        
        // Set animation delay for staggered appearance
        taskDiv.style.animationDelay = `${index * 0.1}s`;
        
        // Create left border indicator based on urgency
        const urgencyLevel = hoursLeft < 12 ? 'bg-yellow-600' : hoursLeft < 24 ? 'bg-yellow-500' : 'bg-yellow-400';
        const indicator = document.createElement('div');
        indicator.className = `absolute top-0 left-0 w-1 h-full ${urgencyLevel} rounded-l-lg`;
        
        // Create task content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'p-3 pl-4';
        
        // Format the deadline date nicely
        const formattedDate = new Intl.DateTimeFormat('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        }).format(deadlineDate);
        
        // Different label based on time remaining
        let timeLabel = '';
        if (hoursLeft < 1) {
          timeLabel = `<span class="font-medium text-yellow-800">Due in less than an hour!</span>`;
        } else if (hoursLeft < 24) {
          timeLabel = `<span class="font-medium text-yellow-800">Due in ${hoursLeft} hours</span>`;
        } else {
          const daysLeft = Math.floor(hoursLeft / 24);
          timeLabel = `<span class="text-yellow-700">Due in ${daysLeft} days</span>`;
        }
        
        contentDiv.innerHTML = `
          <div class="flex justify-between items-start">
            <div class="flex items-center">
              <svg class="w-3 h-3 text-yellow-500 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <div class="text-sm font-medium text-gray-800">${task.title}</div>
            </div>
            <a href="http://127.0.0.1:8000/tasks/task_detail/${orgId}/${task.group_id}/${task.id}/"
              class="opacity-0 group-hover:opacity-100 text-xs px-2 py-1 ml-2 rounded bg-indigo-600 text-white hover:bg-indigo-700 transition-all duration-200 transform group-hover:scale-100 scale-95 flex items-center">
              <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
              </svg>
              View
            </a>
          </div>
          
          <div class="flex items-center text-xs text-gray-500 mt-1">
            <svg class="w-3 h-3 text-gray-400 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
            <span>${task.group__name}</span>
          </div>
          
          <div class="flex justify-between items-center mt-2">
            <div class="flex items-center text-xs">
              <svg class="w-3 h-3 text-yellow-500 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
              <span class="text-gray-600">${formattedDate} (${timeLabel})</span>
            </div>
          </div>
        `;
        
        taskDiv.appendChild(indicator);
        taskDiv.appendChild(contentDiv);
        return taskDiv;
      };
      
      // Render sections by due date groups
      renderSection('Due Today', tasksByDueDate.today, true);
      renderSection('Due Tomorrow', tasksByDueDate.tomorrow);
      renderSection('This Week', tasksByDueDate.thisWeek);
      renderSection('Next Week', tasksByDueDate.nextWeek);
      
      // Add summary at the bottom
      const summaryDiv = document.createElement('div');
      summaryDiv.className = 'mt-4 pt-3 border-t border-gray-200 flex justify-between items-center text-xs text-gray-500';
      summaryDiv.innerHTML = `
        <div class="flex space-x-3">
          ${tasksByDueDate.today.length > 0 ? 
            `<span class="inline-flex items-center"><span class="w-2 h-2 rounded-full bg-yellow-600 mr-1"></span> ${tasksByDueDate.today.length} today</span>` : ''}
          ${tasksByDueDate.tomorrow.length > 0 ? 
            `<span class="inline-flex items-center"><span class="w-2 h-2 rounded-full bg-yellow-500 mr-1"></span> ${tasksByDueDate.tomorrow.length} tomorrow</span>` : ''}
          ${tasksByDueDate.thisWeek.length > 0 ? 
            `<span class="inline-flex items-center"><span class="w-2 h-2 rounded-full bg-yellow-400 mr-1"></span> ${tasksByDueDate.thisWeek.length} this week</span>` : ''}
        </div>
        <a href="#" class="text-indigo-600 hover:text-indigo-800 font-medium">View Calendar</a>
      `;
      container.appendChild(summaryDiv);
    })
    .catch(error => {
      console.error("Error fetching due soon tasks:", error);
      container.innerHTML = `
        <div class="text-center py-6">
          <svg class="w-12 h-12 text-red-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p class="text-sm font-medium text-gray-600">Error loading upcoming tasks</p>
          <p class="text-xs text-gray-500 mt-1">Please try again later</p>
        </div>
      `;
    });
}