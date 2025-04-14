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
        // Update total completed with enhanced styling
        const totalCompleted = document.getElementById('total-completed-count');
        totalCompleted.innerHTML = `
          <div class="flex items-center justify-between mb-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200">
            <div>
              <h3 class="text-2xl font-semibold text-gray-900">${data.total_completed}</h3>
              <p class="text-sm text-gray-600">Total Completed Tasks</p>
            </div>
            <div class="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
          </div>
        `;
  
        const groupContainer = document.getElementById('groupwise-completed-tasks');
        groupContainer.innerHTML = '';
  
        if (data.groupwise.length === 0) {
          groupContainer.innerHTML = `
            <div class="flex flex-col items-center justify-center h-32 text-center p-4">
              <svg class="w-8 h-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <p class="text-sm text-gray-500">No completed tasks by group</p>
            </div>
          `;
          return;
        }
  
        // Container styling with scroll
        groupContainer.classList.add('bg-white', 'rounded-lg', 'shadow-sm', 'border', 'border-gray-200', 'max-h-96', 'overflow-y-auto');
        
        data.groupwise.forEach(group => {
          const groupElement = document.createElement('div');
          groupElement.classList.add(
            'flex',
            'justify-between',
            'items-center',
            'px-4',
            'py-3',
            'hover:bg-gray-50',
            'transition-colors',
            'duration-200',
            'border-b',
            'border-gray-100',
            'last:border-0'
          );
          
          groupElement.innerHTML = `
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span class="text-sm font-normal text-gray-700">${group.group__name}</span>
            </div>
            <span class="text-sm font-medium text-gray-900 px-2 py-1 bg-gray-100 rounded-md">
              ${group.count}
            </span>
          `;
          groupContainer.appendChild(groupElement);
        });
      })
      .catch(error => {
        console.error('Error fetching completed tasks summary:', error);
        document.getElementById('total-completed-count').innerHTML = `
          <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            Failed to load completed tasks
          </div>
        `;
      });
  }

// widget 3 tasks status over time -----------------------------------------------------------------------------------------------------------
function FetchStatusOverTime(orgId) {
    const widget = document.getElementById("status-over-time-widget");
    
    // Apply Tailwind styles to the loading state
    widget.innerHTML = `
      <div class="flex items-center justify-center w-full h-64 rounded-lg bg-gray-50 dark:bg-gray-800">
        <div class="flex flex-col items-center">
          <div class="w-12 h-12 mb-4">
            <svg class="w-full h-full animate-spin text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Loading chart data...</p>
        </div>
      </div>
    `;
    
    fetch(`/tasks_widgets/status-over-time/${orgId}/`)
      .then(response => response.json())
      .then(data => {
        const chartData = data.data;
        
        // Create a styled container for the chart
        widget.innerHTML = `
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 w-full">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200">Task Status Over Time</h3>
              <div class="flex space-x-2">
                
                <button onclick="takeScreenshot('status-over-time-widget')" title="Download Screenshot"
                class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
                   <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </button>
                <button onclick="FetchStatusOverTime(window.djangoData.orgId)" title="Refresh" class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                </button>
                
                <button class="text-gray-500 hover:text-indigo-600 focus:outline-none" title="Settings">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </button>

                <button onclick="openFullScreenWidget('status-over-time-widget')" title="Fullscreen" class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
                    <svg class="w-5 h-5 text-gray-400 hover:text-indigo-600 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                            d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/>
                    </svg>
                </button>
              </div>
            </div>
            <div class="relative">
              <canvas id="statusOverTimeChart" height="280" class="w-full"></canvas>
            </div>
            <div class="flex flex-wrap justify-center mt-4 text-xs font-medium text-gray-600 dark:text-gray-400">
              <div class="time-range-tabs flex bg-gray-100 dark:bg-gray-700 rounded-md p-1">
                <button class="px-3 py-1 rounded-md bg-white dark:bg-gray-800 shadow-sm text-indigo-600 dark:text-indigo-400">7D</button>
                <button class="px-3 py-1 rounded-md hover:bg-white hover:dark:bg-gray-800 hover:text-indigo-600">14D</button>
                <button class="px-3 py-1 rounded-md hover:bg-white hover:dark:bg-gray-800 hover:text-indigo-600">30D</button>
                <button class="px-3 py-1 rounded-md hover:bg-white hover:dark:bg-gray-800 hover:text-indigo-600">3M</button>
                <button class="px-3 py-1 rounded-md hover:bg-white hover:dark:bg-gray-800 hover:text-indigo-600">All</button>
              </div>
            </div>
          </div>
        `;
        
        const ctx = document.getElementById("statusOverTimeChart").getContext("2d");
        
        // Define a modern color palette similar to ClickUp
        const colorPalette = [
          '#7B68EE', // Indigo
          '#00C2E0', // Cyan
          '#FF8A65', // Orange
          '#8BC34A', // Green
          '#FF5722', // Deep Orange
          '#9C27B0', // Purple
          '#FFCA28', // Amber
          '#26A69A'  // Teal
        ];
        
        // Apply the color palette to datasets
        const enhancedDatasets = chartData.datasets.map((ds, index) => ({
          ...ds,
          fill: false,
          borderWidth: 2,
          tension: 0.3,
          borderColor: colorPalette[index % colorPalette.length],
          backgroundColor: colorPalette[index % colorPalette.length],
          pointBackgroundColor: colorPalette[index % colorPalette.length],
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: colorPalette[index % colorPalette.length],
          pointBorderWidth: 2,
          pointHoverRadius: 6,
          pointHoverBorderWidth: 2,
          pointRadius: 4
        }));
        
        new Chart(ctx, {
          type: 'line',
          data: {
            labels: chartData.labels,
            datasets: enhancedDatasets
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: true,
                position: 'top',
                align: 'center',
                labels: {
                  boxWidth: 12,
                  usePointStyle: true,
                  pointStyle: 'circle',
                  padding: 20,
                  font: {
                    family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
                    size: 12,
                    weight: '500'
                  }
                }
              },
              tooltip: {
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                titleColor: '#333',
                bodyColor: '#666',
                bodyFont: {
                  family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
                  size: 12
                },
                titleFont: {
                  family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
                  size: 14,
                  weight: 'bold'
                },
                borderColor: 'rgba(0, 0, 0, 0.1)',
                borderWidth: 1,
                cornerRadius: 8,
                padding: 12,
                boxPadding: 6,
                displayColors: true,
                usePointStyle: true,
                mode: 'index',
                intersect: false
              }
            },
            scales: {
              x: {
                grid: {
                  color: 'rgba(0, 0, 0, 0.05)',
                  drawBorder: false
                },
                ticks: {
                  font: {
                    family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
                    size: 11
                  },
                  color: 'rgba(0, 0, 0, 0.6)'
                }
              },
              y: {
                beginAtZero: true,
                grid: {
                  color: 'rgba(0, 0, 0, 0.05)',
                  drawBorder: false
                },
                ticks: {
                  font: {
                    family: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
                    size: 11
                  },
                  color: 'rgba(0, 0, 0, 0.6)',
                  padding: 10
                }
              }
            },
            interaction: {
              mode: 'nearest',
              intersect: false,
              axis: 'x'
            },
            elements: {
              line: {
                borderWidth: 2,
                tension: 0.4
              }
            },
            layout: {
              padding: {
                top: 5,
                right: 16,
                bottom: 16,
                left: 16
              }
            }
          }
        });
        
        // Add event listeners for tabs
        document.querySelectorAll('.time-range-tabs button').forEach(button => {
          button.addEventListener('click', function() {
            // Remove active class from all buttons
            document.querySelectorAll('.time-range-tabs button').forEach(btn => {
              btn.classList.remove('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-indigo-600', 'dark:text-indigo-400');
            });
            
            // Add active class to clicked button
            this.classList.add('bg-white', 'dark:bg-gray-800', 'shadow-sm', 'text-indigo-600', 'dark:text-indigo-400');
            
            // In a real application, you would fetch new data here based on the selected time range
          });
        });
      })
      .catch(error => {
        console.error('Error fetching status over time:', error);
        
        // Apply Tailwind styles to the error state
        widget.innerHTML = `
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 w-full">
            <div class="flex flex-col items-center justify-center text-center">
              <div class="rounded-full bg-red-100 p-3 mb-4">
                <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">Failed to load chart</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">There was an error retrieving the data. Please try again later.</p>
              <button onclick="FetchStatusOverTime('${orgId}')" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Retry
              </button>
            </div>
          </div>
        `;
      });
  }