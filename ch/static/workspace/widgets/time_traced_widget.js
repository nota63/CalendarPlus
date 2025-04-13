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


// Widget 2) List high priority tasks -------------------------------------------------------------------------------------------------------------------------------------------
function fetchHighPriorityTasks(orgId) {
    fetch(`/time_traced/high-priority-tasks/${orgId}/`)
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById('high-priority-task-list');
        container.innerHTML = '';
  
        if (data.tasks.length === 0) {
          container.innerHTML = `<p class="text-gray-500 text-sm">No high priority tasks 😌</p>`;
          return;
        }
  
        data.tasks.forEach(task => {
          const taskCard = document.createElement('div');
          taskCard.className = "p-3 rounded-lg bg-white border border-red-100 shadow-sm hover:bg-red-50 transition-all duration-150";
  
          taskCard.innerHTML = `
  <div class="p-3 border border-gray-100 rounded-lg bg-white shadow-sm hover:shadow-md transition-all duration-200">
    <div class="flex items-start justify-between mb-2">
      <div class="font-medium text-sm text-gray-800 line-clamp-2">${task.title}</div>
      <div class="ml-2 flex-shrink-0">
        <span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${
          task.status === 'Completed' ? 'bg-green-100 text-green-700' :
          task.status === 'In Progress' ? 'bg-blue-100 text-blue-700' :
          task.status === 'Overdue' ? 'bg-red-100 text-red-700' :
          'bg-gray-100 text-gray-700'
        }">${task.status}</span>
      </div>
    </div>
    
    <div class="flex items-center mb-2">
      <div class="w-full">
        <div class="flex justify-between items-center mb-1">
          <span class="text-xs font-medium text-gray-500">Progress</span>
          <span class="text-xs font-medium text-indigo-600">${task.progress}%</span>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
          <div class="bg-indigo-500 h-full transition-all duration-500 ease-in-out" style="width: ${task.progress}%"></div>
        </div>
      </div>
    </div>
    
    <div class="mt-3 space-y-1.5">
      <div class="flex items-center text-xs">
        <svg class="w-3 h-3 mr-1.5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M8 2h8a2 2 0 0 1 2 2v18a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"></path>
          <path d="M10 18h4"></path>
        </svg>
        <span class="text-gray-600">Group: </span>
        <span class="ml-1 font-medium text-gray-700">${task.group_name}</span>
      </div>
      <div class="flex items-center text-xs">
        <svg class="w-3 h-3 mr-1.5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        <span class="text-gray-600">Deadline: </span>
        <span class="ml-1 font-medium ${
          new Date(task.deadline) < new Date() ? 'text-red-600' : 'text-gray-700'
        }">${task.deadline}</span>
      </div>
    </div>
  </div>`;
  
          container.appendChild(taskCard);
        });
      })
      .catch(error => {
        console.error("Failed to fetch high priority tasks:", error);
      });
  }
  

//  Widget 3) Total Calpoints Earned --------------------------------------------------------------------------------------------------------
function fetchCalPoints(orgId) {
  fetch(`/time_traced/get-calpoints-balance/${orgId}/`)
    .then(response => response.json())
    .then(data => {
      document.getElementById('user-name').textContent = data.username;
      document.getElementById('org-name').textContent = data.organization_name;
      document.getElementById('total-points').textContent = `${data.total_points} pts`;

      const avatar = document.getElementById('user-avatar');
      avatar.src = data.profile_pic || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(data.username);
    })
    .catch(error => {
      console.error('Error loading CalPoints widget:', error);
    });
}


// Fetch calpoints history
function fetchCalpointsHistory(orgId) {
  fetch(`/time_traced/fetch-calpoints-history/${orgId}/`)
      .then(response => response.json())
      .then(data => {
          if (data.error) {
              alert(data.error);
              return;
          }
          
          // Displaying the user's total points in the widget
          document.getElementById('total-points').textContent = data.total_points;

          // Populating the modal with the CalPoints history
          const historyContainer = document.getElementById('calpoints-history');
          historyContainer.innerHTML = ''; // Clear any previous history

          data.history.forEach(item => {
              const historyItem = document.createElement('div');
              historyItem.classList.add('flex', 'justify-between', 'text-sm', 'text-gray-700', 'py-2', 'border-b');
              historyItem.innerHTML = `
              <div class="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors group">
                <!-- Activity Icon -->
                <div class="w-8 h-8 rounded-full bg-indigo-50 flex items-center justify-center mt-1">
                  ${item.type === 'earned' ? 
                    '<i class="fas fa-arrow-up text-indigo-600 text-sm"></i>' :
                    '<i class="fas fa-arrow-down text-red-600 text-sm"></i>'}
                </div>
                
                <!-- Content -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-baseline gap-2">
                    <span class="text-sm font-medium text-gray-900">${item.description}</span>
                    <span class="text-xs ${item.type === 'earned' ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'} px-2 py-1 rounded-full">
                      ${item.type === 'earned' ? '+' : '-'}${item.points} pts
                    </span>
                    <span class="text-xs text-gray-400 ml-auto">${new Date(item.created_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                  
                  <!-- Metadata -->
                  <div class="mt-1 flex items-center gap-2">
                    <span class="text-xs text-gray-500">${new Date(item.created_at).toLocaleDateString()}</span>
                    <div class="w-1 h-1 bg-gray-300 rounded-full"></div>
                    <span class="text-xs text-indigo-600 flex items-center gap-1 cursor-pointer hover:text-indigo-700">
                      <i class="fas fa-link text-[0.6rem]"></i>
                      Source
                    </span>
                  </div>
                </div>
                
                <!-- Status Indicator -->
                <div class="w-2 h-2 rounded-full ${Date.now() - new Date(item.created_at) < 86400000 ? 'bg-green-400' : 'bg-gray-300'} mt-3 ml-2"></div>
              </div>
            `;
              historyContainer.appendChild(historyItem);
          });

          // Displaying the total points in the modal
          document.getElementById('history-total-points').textContent = data.total_points;

          // Show the modal
          var myModal = new bootstrap.Modal(document.getElementById('calpointsHistoryModal'));
          myModal.show();
      })
      .catch(error => {
          console.error('Error fetching CalPoints history:', error);
          alert('Something went wrong. Please try again later.');
      });
}

// widget 4) Embed a Google Doc -----------------------------------------------------------------------------------------------
function fetchGoogleDocEmbed() {
  const docUrl = document.getElementById('doc-url').value;

  fetch('/time_traced/embed-google-doc/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrf_token
    },
    body: `doc_url=${encodeURIComponent(docUrl)}`
  })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert('Error: ' + data.error);
      } else {
        const embedUrl = data.embed_url;
        const modalContent = document.getElementById('modal-embed-content');

        // Set resizable iframe container
        modalContent.innerHTML = `
          <div id="resizable-container" style="
              resize: both;
              overflow: hidden;
              border: 1px solid #ccc;
              width: 100%;
              height: 80vh;
              min-width: 300px;
              min-height: 300px;
          ">
            <iframe 
              src="${embedUrl}" 
              width="100%" 
              height="100%" 
              frameborder="0" 
              style="border: none;"
              allowfullscreen>
            </iframe>
          </div>
        `;

        const modal = new bootstrap.Modal(document.getElementById('embedDocModal'));
        modal.show();
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
}


// widget 5) Google Sheets ----------------------------------------------------------------------------------------------------------------------------
function fetchGoogleSheetEmbed() {
  const sheetUrl = document.getElementById('sheet-url').value;

  fetch('/time_traced/embed-google-sheet/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrf_token
    },
    body: `sheet_url=${encodeURIComponent(sheetUrl)}`
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      alert('Error: ' + data.error);
    } else {
      const embedUrl = data.embed_url;
      const modalContent = document.getElementById('modal-embed-contentt');
      
      modalContent.innerHTML = `
        <div class="w-full h-full relative">
          <iframe 
            src="${embedUrl}" 
            class="absolute top-0 left-0 w-full h-full border-none"
            allowfullscreen>
          </iframe>
        </div>
      `;

      // Initialize the modal and show it
      const modal = new bootstrap.Modal(document.getElementById('embedSheetModal'));
      modal.show();
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}
