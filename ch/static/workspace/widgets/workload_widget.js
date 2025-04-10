
// display pie chart with workload status
function fetchAndRenderUnifiedPieChart(orgId) {
    console.log("📊 Loading Unified Analytics Chart for org:", orgId);
  
    fetch(`/workload/meeting-workload-widget/${orgId}/`)
      .then(response => {
        if (!response.ok) throw new Error("Network response was not OK");
        return response.json();
      })
      .then(data => {
        console.log("📦 Unified Analytics Data:", data);
  
        const combinedLabels = [];
        const combinedValues = [];
        const combinedColors = [];
  
        const colorPalette = [
          "#4ade80", "#60a5fa", "#f87171", "#fbbf24", "#c084fc", "#34d399",
          "#f472b6", "#a3e635", "#facc15", "#38bdf8", "#fb923c", "#818cf8"
        ];
        let colorIndex = 0;
  
        // Merge status, type, location
        const sections = [
          { data: data.status_distribution, prefix: "Status" },
          { data: data.type_distribution, prefix: "Type" },
          { data: data.location_distribution, prefix: "Location" }
        ];
  
        sections.forEach(section => {
          section.data.forEach(item => {
            const label = `${section.prefix}: ${capitalizeFirstLetter(item[Object.keys(item)[0]] || "Unknown")}`;
            const count = item.count;
  
            combinedLabels.push(label);
            combinedValues.push(count);
            combinedColors.push(colorPalette[colorIndex++ % colorPalette.length]);
          });
        });
  
        renderUnifiedPieChart(combinedLabels, combinedValues, combinedColors);
      })
      .catch(error => {
        console.error("❌ Error rendering unified pie chart:", error);
      });
  }
  
  function renderUnifiedPieChart(labels, values, colors) {
    const ctx = document.getElementById("workloadStatusPieChart").getContext("2d");
  
    // Destroy old chart
    if (window.workloadPieChart) {
      window.workloadPieChart.destroy();
    }
  
    window.workloadPieChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderWidth: 1,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              usePointStyle: true,
              padding: 15,
            }
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
  
  function capitalizeFirstLetter(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
  