
// display pie chart with workload status
// Enhanced version of your original JavaScript with Tailwind CSS styling

function fetchAndRenderUnifiedPieChart(orgId) {
    console.log("📊 Loading Unified Analytics Chart for org:", orgId);
    
    // Create or update the container with Tailwind styling
    const chartContainer = document.getElementById("workloadStatusPieChart").parentElement;
    chartContainer.className = "bg-white rounded-lg shadow-md border border-gray-100 p-4 max-w-md mx-auto";
    
    // Add a header to the chart
    let headerElement = document.getElementById("chart-header");
    if (!headerElement) {
      headerElement = document.createElement("div");
      headerElement.id = "chart-header";
      chartContainer.parentNode.insertBefore(headerElement, chartContainer);
    }
    
    headerElement.className = "flex justify-between items-center px-4 py-3 bg-white rounded-t-lg border border-gray-100 border-b-0 max-w-md mx-auto";
    headerElement.innerHTML = `
      <div class="flex items-center space-x-2">
        <div class="w-2 h-2 rounded-full bg-purple-500"></div>
        <h3 class="font-semibold text-gray-800 text-sm">Workload Status</h3>
      </div>
      <div class="flex space-x-2">
        <button id="refreshChartBtn" class="p-1 rounded hover:bg-gray-100" title="Refresh data">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
        <button id="exportChartBtn" class="p-1 rounded hover:bg-gray-100" title="Export data">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
        </button>
        <button id="moreOptionsBtn" class="p-1 rounded hover:bg-gray-100" title="More options">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
          </svg>
        </button>
      </div>
    `;
    
    // Add loading spinner
    let loadingElement = document.getElementById("chart-loading");
    if (!loadingElement) {
      loadingElement = document.createElement("div");
      loadingElement.id = "chart-loading";
      chartContainer.appendChild(loadingElement);
    }
    
    loadingElement.className = "flex justify-center items-center h-64 w-full";
    loadingElement.innerHTML = `<div class="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-500"></div>`;
    loadingElement.style.display = "flex";
    
    // Hide canvas while loading
    const canvas = document.getElementById("workloadStatusPieChart");
    canvas.style.display = "none";
  
    // Set up event listeners for buttons
    document.getElementById("refreshChartBtn").addEventListener("click", () => fetchAndRenderUnifiedPieChart(orgId));
    document.getElementById("exportChartBtn").addEventListener("click", exportChartData);
    document.getElementById("moreOptionsBtn").addEventListener("click", showMoreOptions);
  
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
        
        // Hide loading spinner and show chart
        loadingElement.style.display = "none";
        canvas.style.display = "block";
        
        // Add summary cards
        createSummaryCards(data);
      })
      .catch(error => {
        console.error("❌ Error rendering unified pie chart:", error);
        
        // Show error state
        loadingElement.innerHTML = `
          <div class="flex flex-col items-center justify-center">
            <svg class="w-12 h-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="text-sm text-gray-500 mb-3">Failed to load chart data</p>
            <button class="px-3 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded hover:bg-purple-200" 
                    onclick="fetchAndRenderUnifiedPieChart('${orgId}')">
              Try Again
            </button>
          </div>
        `;
      });
  }
  
  function renderUnifiedPieChart(labels, values, combinedColors) {
    const ctx = document.getElementById("workloadStatusPieChart").getContext("2d");
    
    // Make sure canvas is properly sized and styled
    ctx.canvas.className = "max-h-64";
    
    // Destroy old chart
    if (window.workloadPieChart) {
      window.workloadPieChart.destroy();
    }
    
    // Apply chart.js custom theme
    Chart.defaults.font.family = "'Inter', 'Helvetica', 'Arial', sans-serif";
    Chart.defaults.color = "#4b5563";
    
    window.workloadPieChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: combinedColors,
          borderWidth: 1,
          borderColor: "#ffffff",
          hoverOffset: 5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "65%",
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              usePointStyle: true,
              padding: 15,
              font: {
                size: 11,
                weight: "500"
              },
              color: "#4b5563",
              boxWidth: 8,
              boxHeight: 8
            },
            maxHeight: 100,
            display: true,
            align: "center"
          },
          tooltip: {
            backgroundColor: "rgba(255, 255, 255, 0.95)",
            titleColor: "#111827",
            bodyColor: "#4b5563",
            borderColor: "#e5e7eb",
            borderWidth: 1,
            padding: 12,
            cornerRadius: 6,
            displayColors: true,
            boxWidth: 8,
            boxHeight: 8,
            boxPadding: 3,
            usePointStyle: true,
            callbacks: {
              label: function (context) {
                return `${context.label}: ${context.parsed} meetings`;
              },
              title: function(context) {
                return context[0].label.split(": ")[0];
              }
            }
          }
        },
        animation: {
          animateScale: true,
          animateRotate: true,
          duration: 800
        }
      }
    });
  }
  
  function createSummaryCards(data) {
    // Calculate totals
    let total = 0;
    let completed = 0;
    let pending = 0;
    
    if (data.status_distribution) {
      data.status_distribution.forEach(item => {
        const status = item.status || Object.values(item)[0];
        const count = item.count;
        
        if (status === "completed") {
          completed = count;
        } else if (status === "pending") {
          pending = count;
        }
        total += count;
      });
    }
    
    // Create or update summary element
    const chartContainer = document.getElementById("workloadStatusPieChart").parentElement;
    let summaryElement = document.getElementById("chart-summary");
    
    if (!summaryElement) {
      summaryElement = document.createElement("div");
      summaryElement.id = "chart-summary";
      chartContainer.appendChild(summaryElement);
    }
    
    summaryElement.className = "grid grid-cols-3 gap-2 mt-4";
    summaryElement.innerHTML = `
      <div class="bg-gray-50 rounded p-2 text-center">
        <p class="text-xs text-gray-500">Total</p>
        <p class="font-semibold text-gray-800">${total}</p>
      </div>
      <div class="bg-gray-50 rounded p-2 text-center">
        <p class="text-xs text-gray-500">Completed</p>
        <p class="font-semibold text-green-600">${completed}</p>
      </div>
      <div class="bg-gray-50 rounded p-2 text-center">
        <p class="text-xs text-gray-500">Pending</p>
        <p class="font-semibold text-orange-500">${pending}</p>
      </div>
    `;
  }
  
  function capitalizeFirstLetter(str) {
    if (!str) return "Unknown";
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
  
  // Helper functions for new UI controls
  function exportChartData() {
    // You can implement export functionality here
    console.log("Export chart data");
    alert("Export feature coming soon!");
  }
  
  function showMoreOptions() {
    // Implement more options functionality
    console.log("Show more options");
    alert("More options coming soon!");
  }
  
  // Add font link for Inter font (ClickUp-like font)
  function addFontLink() {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap";
    document.head.appendChild(link);
  }
  
  // Call this when page loads
  document.addEventListener("DOMContentLoaded", function() {
    addFontLink();
    // Detect if Tailwind is already loaded
    if (!document.querySelector('link[href*="tailwindcss"]')) {
      // Add Tailwind CSS if not already present
      const tailwindScript = document.createElement("script");
      tailwindScript.src = "https://cdn.tailwindcss.com";
      document.head.appendChild(tailwindScript);
    }
  });




//Refresh widget for each widget
function refreshWidgetById(widgetId) {
    const widgetEl = document.getElementById(widgetId);
    if (!widgetEl) return console.warn(`🔍 Widget "${widgetId}" not found.`);
  
    let urlTemplate = widgetEl.dataset.refreshUrl;
    if (!urlTemplate) return console.warn(`❌ No URL provided for "${widgetId}"`);
  
    // Replace all placeholders in the URL dynamically
    urlTemplate = urlTemplate.replace(/{(\w+)}/g, (_, key) => {
      return widgetEl.dataset[key] || `{${key}}`;
    });
  
    // Optional loading placeholder
    widgetEl.innerHTML = '<div class="text-center py-4">Refreshing...</div>';
  
    fetch(urlTemplate)
      .then(res => {
        if (!res.ok) throw new Error("Fetch failed");
        return res.text();
      })
      .then(html => {
        widgetEl.innerHTML = html;
        console.log(`✅ Refreshed ${widgetId}`);
      })
      .catch(err => {
        console.error(`❌ Failed to refresh "${widgetId}":`, err);
        widgetEl.innerHTML = '<div class="text-red-500 text-center py-4">Failed to refresh 💔</div>';
      });
  }
  

// Take screenshot of the widget
function takeScreenshot(widgetId) {
    const widget = document.getElementById(widgetId);

    html2canvas(widget, {
        backgroundColor: null,  // Keeps transparency if needed
        scale: 2,               // Higher scale = better quality
    }).then(canvas => {
        const link = document.createElement('a');
        link.download = `${widgetId}-screenshot.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
    }).catch(err => {
        console.error("Screenshot failed:", err);
        alert("Oops! Couldn't take a screenshot.");
    });
}
