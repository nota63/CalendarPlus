function GroupsOverview(orgId) {
    const container = document.getElementById('group-analytics-widget');
    container.innerHTML = `<p>Loading group analytics...</p>`;

    fetch(`/admin_widgets/group-analytics-widget/${orgId}/`)  // replace with actual URL
        .then(response => response.json())
        .then(data => {
            container.innerHTML = ''; // Clear existing content

            data.group_analytics.forEach(group => {
                const groupCard = document.createElement('div');
                groupCard.className = 'group-analytics-card p-4 mb-4 rounded-xl border shadow bg-white';

                // Group Name and Basic Stats
                groupCard.innerHTML = `
                    <h2 class="text-xl font-bold mb-2">${group.group_name}</h2>
                    <p class="text-gray-600 mb-1">Total Tasks: <strong>${group.total_tasks}</strong></p>
                    <p class="text-green-600">Progress: <strong>${group.progress_percent}%</strong></p>

                    <div class="grid grid-cols-2 md:grid-cols-3 gap-2 mt-3 text-sm">
                        <div><strong>✅ Completed:</strong> ${group.completed_tasks}</div>
                        <div><strong>🕒 In Progress:</strong> ${group.in_progress_tasks}</div>
                        <div><strong>⏳ Pending:</strong> ${group.pending_tasks}</div>
                        <div><strong>❌ Cancelled:</strong> ${group.cancelled_tasks}</div>
                        <div><strong>⚠️ Need Changes:</strong> ${group.need_changes}</div>
                        <div><strong>🔒 Pending Approval:</strong> ${group.pending_approval}</div>
                        <div><strong>🔥 Urgent:</strong> ${group.urgent_tasks_count}</div>
                        <div><strong>🚨 Overdue:</strong> ${group.overdue_tasks_count}</div>
                        <div><strong>👥 Active Members:</strong> ${group.active_members_count}</div>
                    </div>

                    <div class="mt-3 text-sm text-gray-700">
                        <p><strong>🗓️ Next Deadline:</strong> ${group.next_deadline ? new Date(group.next_deadline).toLocaleString() : 'N/A'}</p>
                        <p><strong>📅 Latest Deadline:</strong> ${group.latest_deadline ? new Date(group.latest_deadline).toLocaleString() : 'N/A'}</p>
                    </div>

                    <div class="mt-4">
                        <p class="font-semibold text-indigo-600">🏆 Top Contributors:</p>
                        <ul class="list-disc list-inside text-sm text-gray-800">
                            ${group.top_contributors.map(user => `
                                <li>${user.username} — <strong>${user.completed_tasks}</strong> tasks</li>
                            `).join('')}
                        </ul>
                    </div>
                `;

                container.appendChild(groupCard);
            });
        })
        .catch(error => {
            console.error('Analytics fetch failed:', error);
            container.innerHTML = `<p class="text-red-600">Failed to load group analytics. Please try again later.</p>`;
        });
}
