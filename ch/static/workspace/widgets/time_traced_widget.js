function fetchTimeTracing(orgId) {
    const widgetBody = document.querySelector('#timeTracedWidgetBody');
    widgetBody.innerHTML = '<p class="text-sm text-gray-500">Loading...</p>';

    fetch(`/time_traced/get-time-traced-tasks/${orgId}/`)
        .then(response => response.json())
        .then(data => {
            widgetBody.innerHTML = '';

            if (data.success && data.data.length > 0) {
                data.data.forEach(entry => {
                    const item = `
                        <div class="mb-3 p-3 bg-white border border-gray-200 rounded-lg shadow-sm">
                            <div class="text-sm font-semibold text-gray-800">${entry.task_title}</div>
                            <div class="text-xs text-gray-600 mt-1">
                                <span class="block">🕐 Start: ${entry.start_time}</span>
                                <span class="block">⏰ End: ${entry.end_time}</span>
                                <span class="block">⏳ Duration: <strong>${entry.duration} hrs</strong></span>
                                <span class="block">📊 Time Tracked: <strong>${entry.time_spent} hrs</strong></span>
                            </div>
                        </div>
                    `;
                    widgetBody.innerHTML += item;
                });
            } else {
                widgetBody.innerHTML = '<p class="text-sm text-gray-500">No time tracking data available for your tasks.</p>';
            }
        })
        .catch(error => {
            widgetBody.innerHTML = '<p class="text-sm text-red-500">Failed to load time tracking data.</p>';
            console.error('Time Tracking Widget Error:', error);
        });
}
