function fetchAndRenderProgress(orgId) {
    const widget = document.getElementById('progress-widget');
    if (!widget) return;
  
    fetch(`/progress/user-task-progress-widget/${orgId}/`)
      .then(response => response.json())
      .then(data => {
        const container = widget.querySelector(".task-progress-container");
        container.innerHTML = "";
  
        if (data.tasks.length === 0) {
          container.innerHTML = "<p class='text-sm text-gray-400'>No tasks assigned.</p>";
          return;
        }
  
        data.tasks.forEach(task => {
          const taskBlock = document.createElement("div");
          taskBlock.className = "mb-4 relative";
  
          // Title
          const titleDiv = document.createElement("div");
          titleDiv.className = "text-sm font-medium text-gray-700 cursor-pointer tooltip-anchor";
          titleDiv.textContent = task.title;
  
          // Group
          const groupDiv = document.createElement("div");
          groupDiv.className = "text-xs text-gray-400 mb-1";
          groupDiv.textContent = `Group: ${task.group__name}`;
  
          // Progress bar
          const progressBarContainer = document.createElement("div");
          progressBarContainer.className = "w-full bg-gray-100 rounded-full h-2.5";
          const progressBar = document.createElement("div");
          progressBar.className = "bg-indigo-500 h-2.5 rounded-full transition-all duration-500 ease-in-out";
          progressBar.style.width = `${task.progress}%`;
          progressBarContainer.appendChild(progressBar);
  
          const percentText = document.createElement("div");
          percentText.className = "text-right text-xs text-gray-500 mt-1";
          percentText.textContent = `${task.progress}%`;
  
          // Tooltip logic - attach inside closure (SAFE)
          titleDiv.addEventListener("mouseenter", () => {
            fetch(`/progress/get-task-progress-details/${orgId}/${task.id}/`)
              .then(res => res.json())
              .then(data => {
                const tooltip = document.createElement("div");
                tooltip.className = "absolute z-50 bg-white border border-gray-300 text-xs p-2 rounded shadow-md tooltip-box";
  
                const rect = titleDiv.getBoundingClientRect();
                tooltip.style.top = `${rect.top + window.scrollY + 24}px`;
                tooltip.style.left = `${rect.left + window.scrollX}px`;
  
                tooltip.innerHTML = `
                  <div><strong>Assigned By:</strong> ${data.assigned_by}</div>
                  <div><strong>Deadline:</strong> ${data.deadline}</div>
                  <div><strong>Remaining Days:</strong> ${data.remaining_days}</div>
                  <div><strong>Subtasks:</strong> ${data.subtasks.completed} / ${data.subtasks.total}</div>
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
          taskBlock.appendChild(percentText);
          container.appendChild(taskBlock);
        });
      })
      .catch(error => {
        console.error("Error fetching progress:", error);
      });
  }
  