
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
            <div class="border rounded px-3 py-2 mb-2 shadow-sm bg-light" data-group-id="${group.id}">
              <strong>${group.name}</strong>
            </div>
          `).join("");
          groupListEl.innerHTML = groupHtml;
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
          taskEl.className = 'border rounded p-3 mb-2 shadow-sm d-flex justify-content-between align-items-center';
  
          taskEl.innerHTML = `
            <div>
              <strong>${task.title}</strong><br>
              <small>Status: ${task.status} | Priority: ${task.priority} | Deadline: ${task.deadline}</small>
            </div>
            <div>
              <a href="/tasks/task_detail/${orgId}/${groupId}/${task.id}/" 
                 class="btn btn-sm btn-primary" target="_blank">
                🚀 Launch
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
  