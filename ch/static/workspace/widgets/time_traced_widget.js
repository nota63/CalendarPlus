function fetchTimeTracing(orgId) {
    const widgetBody = document.querySelector('#timeTracedWidgetBody');
    widgetBody.innerHTML = '<p class="text-sm text-gray-500">Loading...</p>';

    fetch(`/time_traced/get-time-traced-tasks/${orgId}/`)
        .then(response => response.json())
        .then(data => {
            widgetBody.innerHTML = '';

            if (data.success && data.data.length > 0) {
                data.data.forEach(entry => {
                    const item = `
  <div class="mb-3 p-4 bg-white border border-gray-200 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 cursor-pointer">
    <div class="flex justify-between items-start">
      <div class="flex-grow">
        <div class="text-base font-medium text-indigo-900">${entry.task_title}</div>
        <div class="mt-2 grid grid-cols-2 gap-2 text-xs">
          <div class="flex items-center text-gray-600">
            <svg class="w-3.5 h-3.5 mr-1.5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            <span class="font-medium">Start:</span> 
            <span class="ml-1 text-gray-700">${entry.start_time}</span>
          </div>
          <div class="flex items-center text-gray-600">
            <svg class="w-3.5 h-3.5 mr-1.5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 8 10"></polyline>
            </svg>
            <span class="font-medium">End:</span> 
            <span class="ml-1 text-gray-700">${entry.end_time}</span>
          </div>
          <div class="flex items-center text-gray-600">
            <svg class="w-3.5 h-3.5 mr-1.5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2v4"></path>
              <path d="M12 18v4"></path>
              <path d="M4.93 4.93l2.83 2.83"></path>
              <path d="M16.24 16.24l2.83 2.83"></path>
              <path d="M2 12h4"></path>
              <path d="M18 12h4"></path>
              <path d="M4.93 19.07l2.83-2.83"></path>
              <path d="M16.24 7.76l2.83-2.83"></path>
            </svg>
            <span class="font-medium">Duration:</span> 
            <span class="ml-1 text-indigo-600 font-semibold">${entry.duration} hrs</span>
          </div>
          <div class="flex items-center text-gray-600">
            <svg class="w-3.5 h-3.5 mr-1.5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 20v-6"></path>
              <path d="M6 20v-12"></path>
              <path d="M18 20v-3"></path>
              <rect x="2" y="2" width="20" height="4" rx="1"></rect>
              <rect x="2" y="20" width="20" height="2" rx="1"></rect>
            </svg>
            <span class="font-medium">Time Tracked:</span> 
            <span class="ml-1 text-indigo-600 font-semibold">${entry.time_spent} hrs</span>
          </div>
        </div>
      </div>
      <div class="ml-2 flex flex-shrink-0">
        <div class="w-2 h-2 rounded-full bg-green-500"></div>
      </div>
    </div>
  </div>`;
                    widgetBody.innerHTML += item;
                });
            } else {
                widgetBody.innerHTML = '<p class="text-sm text-gray-500">No time tracking data available for your tasks.</p>';
            }
        })
        .catch(error => {
            widgetBody.innerHTML = '<p class="text-sm text-red-500">Failed to load time tracking data.</p>';
            console.error('Time Tracking Widget Error:', error);
        });
}
