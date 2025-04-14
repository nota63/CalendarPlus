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
      // Update total completed
      document.getElementById('total-completed-count').textContent = `${data.total_completed} tasks completed`;

      const groupContainer = document.getElementById('groupwise-completed-tasks');
      groupContainer.innerHTML = '';

      if (data.groupwise.length === 0) {
        groupContainer.innerHTML = '<p class="text-sm text-gray-500">No completed tasks by group.</p>';
        return;
      }

      // Inject each group with count
      data.groupwise.forEach(group => {
        const groupElement = document.createElement('div');
        groupElement.classList.add('text-sm', 'text-gray-800', 'flex', 'justify-between', 'border-b', 'py-1');
        groupElement.innerHTML = `
          <span>${group.group__name}</span>
          <span class="font-medium">${group.count}</span>
        `;
        groupContainer.appendChild(groupElement);
      });
    })
    .catch(error => {
      console.error('Error fetching completed tasks summary:', error);
      document.getElementById('total-completed-count').textContent = 'Failed to load';
    });
}



