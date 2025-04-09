
// Fetch and display the groups

// Fetch and display the groups
function fetchAndRenderUserGroups(orgId) {
  const groupListEl = document.getElementById("group-list");
  if (!groupListEl) {
    console.warn("🚫 group-list element not found");
    return;
  }

  const endpoint = `/widgets/get-user-groups-json/?org_id=${orgId}`;
  console.log("📡 Fetching groups from:", endpoint);

  fetch(endpoint)
    .then(response => {
      if (!response.ok) throw new Error(`Server returned ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (data.groups && data.groups.length > 0) {
        const groupHtml = data.groups.map(group => `
          <div class="bg-white border border-gray-200 rounded-lg p-4 mb-3 shadow-xs hover:shadow-sm transition-shadow group"
               data-group-id="${group.id}">
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <h3 class="font-semibold text-gray-800 text-base mb-1">${group.name}</h3>
                <div class="flex items-center space-x-2">
                  <span class="inline-flex items-center justify-center w-8 h-8 bg-indigo-500 text-white rounded-full text-sm font-medium">
                    ${group.team_leader ? group.team_leader.charAt(0).toUpperCase() : '?'}
                  </span>
                  <span class="text-sm text-gray-600">${group.team_leader || 'No leader'}</span>
                </div>
              </div>
              <div class="ml-4 flex items-center space-x-3">
                <span class="text-xs font-medium px-2 py-1 rounded-full bg-green-50 text-green-700">
                  ${group.member_count} members
                </span>
                <!-- 📅 Calendar View trigger -->
            <button class="btn btn-sm btn-outline-primary calendar-view-btn"
                    data-group-id="${group.id}"
                    data-org-id="${orgId}"
                    data-bs-toggle="modal"
                    data-bs-target="#groupCalendarModal"
                    title="View Calendar">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" class="bi bi-calendar">
                <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/>
                <path d="M2.5 5a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H3a.5.5 0 0 1-.5-.5v-1z"/>
              </svg>
            </button>
            </div>
            </div>
          </div>
        `).join("");

        groupListEl.innerHTML = groupHtml;

        // 🎯 Attach click event to calendar view buttons
        document.querySelectorAll('.calendar-view-btn').forEach(btn => {
          btn.addEventListener('click', function () {
            const groupId = this.getAttribute('data-group-id');
            const orgId = this.getAttribute('data-org-id');
            loadGroupCalendar(groupId, orgId);
          });
        });

      } else {
        groupListEl.innerHTML = `<p class="text-muted">No groups found for you in this organization.</p>`;
      }
    })
    .catch(error => {
      console.error("❌ Error fetching groups:", error);
      groupListEl.innerHTML = `
        <div class="alert alert-danger">
          Failed to load groups.<br><code>${error.message}</code>
        </div>
      `;
    });
}




  
// ⏳ Wait until DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
    const orgId = window.djangoData.orgId;
    if (orgId) {
      fetchAndRenderUserGroups(orgId);
  
      // Delay click listener attachment to allow groups to render
      setTimeout(() => attachGroupClickListeners(orgId), 800);
    }
  });
  
  // ✨ Attach click events to group elements
  function attachGroupClickListeners(orgId) {
    document.querySelectorAll('#group-list .border').forEach(groupEl => {
      groupEl.addEventListener('click', function () {
        const groupName = this.querySelector('strong')?.innerText || "Group";
        const groupId = this.dataset.groupId || this.getAttribute('data-group-id');
  
        if (!groupId) {
          alert("Group ID missing. Please ensure it's rendered correctly.");
          return;
        }
  
        console.log(`🟢 Group Clicked: ${groupName} | ID: ${groupId}`);
        fetchAndShowGroupTasks(orgId, groupId, groupName);
      });
    });
  }
  
  // 🚀 Fetch and display tasks inside the modal
  function fetchAndShowGroupTasks(orgId, groupId, groupName) {
    const modalTitle = document.getElementById('groupTasksModalLabel');
    const content = document.getElementById('groupTasksContent');
  
    if (modalTitle) modalTitle.textContent = `${groupName} Tasks`;
    content.innerHTML = `<p class="text-muted">Loading tasks...</p>`;
  
    const endpoint = `/widgets/get-user-tasks-by-group/?org_id=${orgId}&group_id=${groupId}`;
    fetch(endpoint)
      .then(res => {
        if (!res.ok) throw new Error(`Status ${res.status}`);
        return res.json(); // 👉 Expecting JSON now
      })
      .then(data => {
        content.innerHTML = ''; // Clear previous content
  
        if (!data.tasks || data.tasks.length === 0) {
          content.innerHTML = `<div class="alert alert-info">No tasks assigned to you in this group.</div>`;
          return;
        }
  
        data.tasks.forEach(task => {
          const taskEl = document.createElement('div');
          taskEl.className = 'bg-white border border-gray-200 rounded-lg p-4 mb-3 shadow-xs hover:shadow-sm transition-shadow flex items-center justify-between group';

taskEl.innerHTML = `
  <div class="flex-1 space-y-1.5">
    <h3 class="font-semibold text-gray-800 text-base leading-tight">${task.title}</h3>
    <div class="flex items-center space-x-3 text-sm">
      <span class="inline-flex items-center text-gray-500">
        <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        ${task.status}
      </span>
      <span class="inline-flex items-center text-gray-500">
        <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343M7 11h10m-5 5v-5"/>
        </svg>
        ${task.priority}
      </span>
      <span class="inline-flex items-center text-gray-500">
        <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
        ${task.deadline}
      </span>
    </div>
  </div>
  <div class="ml-4">
    <a href="/tasks/task_detail/${orgId}/${groupId}/${task.id}/" 
       class="p-2 hover:bg-gray-50 rounded-md transition-colors border border-gray-200 hover:border-gray-300"
       target="_blank"
       aria-label="Launch task">
      <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
      </svg>
    </a>
  </div>
`;
          content.appendChild(taskEl);
        });
      })
      .catch(err => {
        content.innerHTML = `
          <div class="alert alert-danger">
            Could not load tasks.<br><code>${err.message}</code>
          </div>`;
      })
      .finally(() => {
        const modal = new bootstrap.Modal(document.getElementById('groupTasksModal'));
        modal.show();
      });
  }

// Initialize Full Calendar
function loadGroupCalendar(groupId, orgId) {
  const calendarEl = document.getElementById('groupCalendar');
  if (!calendarEl) return;

  // Clear previous calendar instance if exists
  if (calendarEl.innerHTML.trim()) {
    calendarEl.innerHTML = '';
  }

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    themeSystem: 'bootstrap5',
    height: 'auto',
    events: `/widgets/group-tasks-calendar-view/?org_id=${orgId}&group_id=${groupId}`,
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,listWeek'
    },
    eventColor: '#4f46e5'
  });

  calendar.render();
}
