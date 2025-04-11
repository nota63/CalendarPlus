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
        <h3 class="text-base font-semibold text-indigo-700">Task Progress</h3>
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