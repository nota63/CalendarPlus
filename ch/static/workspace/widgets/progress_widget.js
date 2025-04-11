function fetchAndRenderProgress(orgId) {
    const widget = document.getElementById('progress-widget');
    if (!widget) return;
  
    fetch(`/progress/user-task-progress-widget/${orgId}/`)
      .then(response => response.json())
      .then(data => {
        const container = widget.querySelector(".task-progress-container");
        container.innerHTML = ""; // Clear previous entries
  
        if (data.tasks.length === 0) {
          container.innerHTML = "<p class='text-sm text-gray-400'>No tasks assigned.</p>";
          return;
        }
  
        data.tasks.forEach(task => {
          const taskBlock = document.createElement("div");
          taskBlock.className = "mb-4";
  
          taskBlock.innerHTML = `
            <div class="text-sm font-medium text-gray-700">${task.title}</div>
            <div class="text-xs text-gray-400 mb-1">Group: ${task.group__name}</div>
            <div class="w-full bg-gray-100 rounded-full h-2.5">
              <div class="bg-indigo-500 h-2.5 rounded-full transition-all duration-500 ease-in-out" style="width: ${task.progress}%"></div>
            </div>
            <div class="text-right text-xs text-gray-500 mt-1">${task.progress}%</div>
          `;
  
          container.appendChild(taskBlock);
        });
      })
      .catch(error => {
        console.error("Error fetching progress:", error);
      });
  }
  