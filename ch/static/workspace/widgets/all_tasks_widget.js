function fetchTasksProgressCount(orgId) {
    const countDisplay = document.getElementById('in-progress-task-count');
    countDisplay.textContent = '...';
  
    fetch(`/tasks_widgets/tasks-in-progress/${orgId}/`)
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          countDisplay.textContent = 'Err';
          console.error('Error fetching task count:', data.error);
        } else {
            countDisplay.textContent = data.count;
        }
      })
      .catch(error => {
        countDisplay.textContent = 'Err';
        console.error('Fetch failed:', error);
      });
  }


// Widget 2 Completed Tasks Per Group------------------------------------------------------------------------------------------------------------------
function FetchCompletedTasksSummary(orgId) {
    fetch(`/tasks_widgets/completed-tasks-summary/${orgId}/`)
      .then(response => response.json())
      .then(data => {
        // Update total completed with enhanced styling
        const totalCompleted = document.getElementById('total-completed-count');
        totalCompleted.innerHTML = `
          <div class="flex items-center justify-between mb-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200">
            <div>
              <h3 class="text-2xl font-semibold text-gray-900">${data.total_completed}</h3>
              <p class="text-sm text-gray-600">Total Completed Tasks</p>
            </div>
            <div class="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
          </div>
        `;
  
        const groupContainer = document.getElementById('groupwise-completed-tasks');
        groupContainer.innerHTML = '';
  
        if (data.groupwise.length === 0) {
          groupContainer.innerHTML = `
            <div class="flex flex-col items-center justify-center h-32 text-center p-4">
              <svg class="w-8 h-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <p class="text-sm text-gray-500">No completed tasks by group</p>
            </div>
          `;
          return;
        }
  
        // Container styling with scroll
        groupContainer.classList.add('bg-white', 'rounded-lg', 'shadow-sm', 'border', 'border-gray-200', 'max-h-96', 'overflow-y-auto');
        
        data.groupwise.forEach(group => {
          const groupElement = document.createElement('div');
          groupElement.classList.add(
            'flex',
            'justify-between',
            'items-center',
            'px-4',
            'py-3',
            'hover:bg-gray-50',
            'transition-colors',
            'duration-200',
            'border-b',
            'border-gray-100',
            'last:border-0'
          );
          
          groupElement.innerHTML = `
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span class="text-sm font-normal text-gray-700">${group.group__name}</span>
            </div>
            <span class="text-sm font-medium text-gray-900 px-2 py-1 bg-gray-100 rounded-md">
              ${group.count}
            </span>
          `;
          groupContainer.appendChild(groupElement);
        });
      })
      .catch(error => {
        console.error('Error fetching completed tasks summary:', error);
        document.getElementById('total-completed-count').innerHTML = `
          <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            Failed to load completed tasks
          </div>
        `;
      });
  }