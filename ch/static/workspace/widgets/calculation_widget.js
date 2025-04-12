
// Fetch and render the calculations
// 🧠 Fetch and render the calculation widget data
function fetchAndRenderCalculationWidget(orgId) {
    console.log("📡 Fetching calculation data for org ID:", orgId);
  
    fetch(`/calculation/get-calculation/${orgId}/`)
      .then(response => {
        console.log("📬 Received response:", response);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log("📊 Parsed data:", data);
  
        // Update DOM elements
        document.getElementById("total-tasks-count").textContent = data.total_tasks;
        document.getElementById("total-meetings-count").textContent = data.total_meetings;
        document.getElementById("total-events-count").textContent = data.total_events;
        document.getElementById("total-bookings-count").textContent = data.total_bookings;
  
        console.log("✅ Calculation widget updated successfully!");
      })
      .catch(error => {
        console.error("❌ Error loading calculation widget data:", error);
      });
  }
  

// Open in full screen
// Open in full screen
function openFullScreenWidget(widgetId) {
  const widget = document.getElementById(widgetId);

  // Overlay setup
  let overlay = document.getElementById('widgetOverlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'widgetOverlay';
    overlay.className = 'fixed inset-0 bg-gray-800 bg-opacity-30 backdrop-blur-sm z-[900] opacity-0 transition-opacity duration-300';
    document.body.appendChild(overlay);
    requestAnimationFrame(() => overlay.classList.add('opacity-100'));
  } else {
    overlay.classList.remove('hidden');
    overlay.classList.add('opacity-100');
  }

  // Style the widget as a fullscreen modal
  widget.classList.add(
    'fixed', 'top-[5%]', 'left-1/2', 'transform', '-translate-x-1/2',
    'w-[99%]', 'h-[90%]', 'bg-white', 'z-[100]', 'rounded-xl', 'shadow-2xl',
    'overflow-y-auto', 'transition-all', 'duration-300', 'p-6'
  );

  // Set highest z-index and escape any nesting issues
  widget.style.position = 'fixed';
  widget.style.zIndex = '1000';
  widget.style.maxWidth = '1280px';
  
  // Animate in
  requestAnimationFrame(() => {
    widget.classList.remove('scale-95', 'opacity-0');
    widget.classList.add('scale-100', 'opacity-100');
  });

  // Add close button if not there
  if (!document.getElementById('fullscreenCloseBtn')) {
    const closeBtn = document.createElement('button');
    closeBtn.id = 'fullscreenCloseBtn';
    closeBtn.innerHTML = '&times;';
    closeBtn.className = 'absolute top-4 right-5 text-3xl text-gray-400 hover:text-black z-[1010]';
    closeBtn.onclick = () => closeFullScreenWidget(widgetId);
    widget.appendChild(closeBtn);
  }

  // Lock background scroll
  document.body.classList.add('overflow-hidden');

  console.log("✨ Fullscreen modal opened:", widgetId);
}

function closeFullScreenWidget(widgetId) {
  const widget = document.getElementById(widgetId);
  const overlay = document.getElementById('widgetOverlay');
  const closeBtn = document.getElementById('fullscreenCloseBtn');

  widget.classList.remove(
    'fixed', 'top-[5%]', 'left-1/2', 'transform', '-translate-x-1/2',
    'w-[95%]', 'h-[90%]', 'bg-white', 'z-[100]', 'rounded-xl', 'shadow-2xl',
    'overflow-y-auto', 'transition-all', 'duration-300', 'p-6'
  );
  widget.style.position = '';
  widget.style.zIndex = '';

  if (overlay) overlay.classList.add('hidden');
  if (closeBtn) closeBtn.remove();
  document.body.classList.remove('overflow-hidden');

  console.log("🛑 Fullscreen modal closed:", widgetId);
}







  
// Fetch Tasks Analytics
function fetchAndRenderTaskAnalytics(orgId) {
  console.log("📡 Fetching task analytics for org:", orgId);

  // Show the modal first
  const taskModal = new bootstrap.Modal(document.getElementById("taskAnalyticsModal"));
  taskModal.show();

  // Inject temporary loading state
  document.getElementById("task-analytics-modal-body").innerHTML = `
    <div class="flex justify-center items-center p-8">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto mb-4"></div>
        <p class="text-gray-500 font-medium">Loading task analytics...</p>
      </div>
    </div>
  `;

  fetch(`/calculation/get-task-analytics/${orgId}/`)
    .then((response) => {
      if (!response.ok) throw new Error("Network response not ok");
      return response.json();
    })
    .then((data) => {
      console.log("📦 Task Analytics Fetched:", data);
      
      const html = `
        <div class="bg-gray-50 rounded-lg shadow-sm p-4">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Task Overview</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <!-- Key Metrics Cards -->
            <div class="bg-white rounded-lg shadow-sm p-4 border-l-4 border-green-500">
              <div class="flex justify-between items-center">
                <div>
                  <p class="text-sm font-medium text-gray-500">Completion Rate</p>
                  <p class="text-2xl font-bold text-gray-800">${data.completion_rate}%</p>
                </div>
                <div class="bg-green-100 p-3 rounded-full">
                  <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-sm p-4 border-l-4 border-blue-500">
              <div class="flex justify-between items-center">
                <div>
                  <p class="text-sm font-medium text-gray-500">Average Progress</p>
                  <p class="text-2xl font-bold text-gray-800">${data.average_progress}%</p>
                </div>
                <div class="bg-blue-100 p-3 rounded-full">
                  <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg shadow-sm p-5 mb-6">
            <h4 class="text-md font-medium text-gray-700 mb-4">Task Status Distribution</h4>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="text-center">
                <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 mb-2">
                  <span class="text-green-600 text-lg">✓</span>
                </div>
                <h5 class="text-2xl font-semibold text-gray-800">${data.completed_tasks}</h5>
                <p class="text-xs text-gray-500 font-medium">Completed</p>
              </div>

               <div class="text-center">
                <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-indigo-100 mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                </div>

                <h5 class="text-2xl font-semibold text-gray-800">${data.total_tasks}</h5>
                <p class="text-xs text-gray-500 font-medium">Total Tasks</p>
              </div>
              
              <div class="text-center">
                <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-yellow-100 mb-2">
                  <span class="text-yellow-600 text-lg">⌛</span>
                </div>
                <h5 class="text-2xl font-semibold text-gray-800">${data.pending_tasks}</h5>
                <p class="text-xs text-gray-500 font-medium">Pending</p>
              </div>
              
              <div class="text-center">
                <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 mb-2">
                  <span class="text-blue-600 text-lg">🚧</span>
                </div>
                <h5 class="text-2xl font-semibold text-gray-800">${data.in_progress_tasks}</h5>
                <p class="text-xs text-gray-500 font-medium">In Progress</p>
              </div>
              
              <div class="text-center">
                <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mb-2">
                  <span class="text-red-600 text-lg">🔥</span>
                </div>
                <h5 class="text-2xl font-semibold text-gray-800">${data.overdue_tasks}</h5>
                <p class="text-xs text-gray-500 font-medium">Overdue</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg shadow-sm mb-2">
            <div class="p-4 border-b border-gray-100">
              <h4 class="text-md font-medium text-gray-700">Timeline Overview</h4>
            </div>
            
            <div class="p-4">
              <div class="flex items-center py-2 border-b border-gray-100">
                <div class="bg-red-100 p-2 rounded-md mr-3">
                  <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <div class="flex-grow">
                  <span class="text-gray-600 font-medium">Urgent Tasks</span>
                </div>
                <div class="text-xl font-bold text-gray-800">${data.urgent_tasks}</div>
              </div>
              
              <div class="flex items-center py-2 border-b border-gray-100">
                <div class="bg-amber-100 p-2 rounded-md mr-3">
                  <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                </div>
                <div class="flex-grow">
                  <span class="text-gray-600 font-medium">Due Today</span>
                </div>
                <div class="text-xl font-bold text-gray-800">${data.tasks_due_today}</div>
              </div>
              
              <div class="flex items-center py-2">
                <div class="bg-indigo-100 p-2 rounded-md mr-3">
                  <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                </div>
                <div class="flex-grow">
                  <span class="text-gray-600 font-medium">Due This Week</span>
                </div>
                <div class="text-xl font-bold text-gray-800">${data.tasks_due_this_week}</div>
              </div>
            </div>
          </div>
        </div>
      `;
      
      document.getElementById("task-analytics-modal-body").innerHTML = html;
    })
    .catch((error) => {
      console.error("❌ Task Analytics Fetch Failed:", error);
      document.getElementById("task-analytics-modal-body").innerHTML = `
        <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Error Loading Analytics</h3>
              <div class="mt-2 text-sm text-red-700">
                <p>Could not load task analytics. Please try again later.</p>
              </div>
            </div>
          </div>
        </div>
      `;
    });
}