
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
  