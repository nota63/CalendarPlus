
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
function openFullScreenWidget(widgetId) {
    const elem = document.getElementById(widgetId);
    if (elem.requestFullscreen) {
      elem.requestFullscreen();
    } else if (elem.webkitRequestFullscreen) { // Safari
      elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { // IE11
      elem.msRequestFullscreen();
    }
    console.log("🔍 Widget opened in fullscreen:", widgetId);
  }
  

// Fetch Tasks Analytics
function fetchAndRenderTaskAnalytics(orgId) {
    console.log("📡 Fetching task analytics for org:", orgId);
  
    // Show the modal first
    const taskModal = new bootstrap.Modal(document.getElementById("taskAnalyticsModal"));
    taskModal.show();
  
    // Inject temporary loading state
    document.getElementById("task-analytics-modal-body").innerHTML = `<p class="text-muted">⏳ Loading task stats...</p>`;
  
    fetch(`/calculation/get-task-analytics/${orgId}/`)
      .then((response) => {
        if (!response.ok) throw new Error("Network response not ok");
        return response.json();
      })
      .then((data) => {
        console.log("📦 Task Analytics Fetched:", data);
        const html = `
          <ul class="list-group list-group-flush">
            <li class="list-group-item">✔️ <strong>Completed Tasks:</strong> ${data.completed_tasks}</li>
            <li class="list-group-item">⌛ <strong>Pending Tasks:</strong> ${data.pending_tasks}</li>
            <li class="list-group-item">🚧 <strong>In Progress:</strong> ${data.in_progress_tasks}</li>
            <li class="list-group-item">🔥 <strong>Overdue Tasks:</strong> ${data.overdue_tasks}</li>
            <li class="list-group-item">🚨 <strong>Urgent Tasks:</strong> ${data.urgent_tasks}</li>
            <li class="list-group-item">📅 <strong>Due Today:</strong> ${data.tasks_due_today}</li>
            <li class="list-group-item">📆 <strong>Due This Week:</strong> ${data.tasks_due_this_week}</li>
            <li class="list-group-item">📈 <strong>Completion Rate:</strong> ${data.completion_rate}%</li>
            <li class="list-group-item">📊 <strong>Average Progress:</strong> ${data.average_progress}%</li>
          </ul>
        `;
        document.getElementById("task-analytics-modal-body").innerHTML = html;
      })
      .catch((error) => {
        console.error("❌ Task Analytics Fetch Failed:", error);
        document.getElementById("task-analytics-modal-body").innerHTML = `<div class="alert alert-danger">Could not load task analytics. Please try again later.</div>`;
      });
  }
  