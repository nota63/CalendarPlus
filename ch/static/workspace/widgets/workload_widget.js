
// display pie chart with workload status
function fetchAndRenderPieChart(orgId) {
    console.log("📊 Initializing Workload by Status chart for org:", orgId);
  
    fetch(`/workload/meeting-workload-widget/${orgId}/`)
      .then(response => {
        if (!response.ok) throw new Error("Network response was not OK");
        return response.json();
      })
      .then(data => {
        console.log("📦 Analytics Data Received:", data);
  
        const statusData = data.status_distribution;
  
        if (!statusData || statusData.length === 0) {
          console.warn("🚨 No meeting status data found!");
          return;
        }
  
        const labels = statusData.map(item => capitalizeFirstLetter(item.status || "Unknown"));
        const values = statusData.map(item => item.count);
  
        renderPieChart(labels, values);
      })
      .catch(error => {
        console.error("❌ Error fetching meeting status analytics:", error);
      });
  }
  
  function renderPieChart(labels, values) {
    const ctx = document.getElementById("workloadStatusPieChart").getContext("2d");
  
    // Clear old chart if exists
    if (window.workloadPieChart) {
      window.workloadPieChart.destroy();
    }
  
    window.workloadPieChart = new Chart(ctx, {
      type: "pie",
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: [
            "#4ade80", // Scheduled - Green
            "#60a5fa", // Completed - Blue
            "#f87171", // Canceled - Red
            "#fbbf24", // Other - Yellow
          ],
          borderWidth: 1,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "bottom",
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `${context.label}: ${context.parsed} meetings`;
              }
            }
          }
        }
      }
    });
  }
  
  // Optional utility to beautify labels
  function capitalizeFirstLetter(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
  






























