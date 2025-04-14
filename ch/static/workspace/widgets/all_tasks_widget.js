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
  