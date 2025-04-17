function fetchAndDisplayGroups(orgId) {
    const container = document.getElementById('group-analytics-widget');
    container.innerHTML = `<p>Loading groups...</p>`;  // Show loading text initially

    // Fetch group leader info from the server
    fetch(`/admin_widgets/list-groups/${orgId}/`)  // Replace with the correct URL
        .then(response => response.json())
        .then(data => {
            container.innerHTML = '';  // Clear existing content

            // Check if groups are available
            if (data.groups && data.groups.length > 0) {
                data.groups.forEach(group => {
                    const groupCard = document.createElement('div');
                    groupCard.className = 'group-card p-4 mb-4 rounded-xl border shadow bg-white';

                    // Create the group leader card content
                    groupCard.innerHTML = `
                        <h2 class="text-xl font-bold mb-2">${group.group_name}</h2>
                        <div class="flex items-center mb-3">
                            <img src="${group.team_leader.profile_picture || '/static/default-profile-pic.jpg'}" 
                                 alt="${group.team_leader.username}" 
                                 class="w-12 h-12 rounded-full mr-3">
                            <div>
                                <p class="font-semibold">${group.team_leader.username}</p>
                                <p class="text-gray-600 text-sm">Team Leader</p>
                            </div>
                        </div>
                    `;

                    container.appendChild(groupCard);
                });
            } else {
                container.innerHTML = `<p>No groups found for this organization.</p>`;
            }
        })
        .catch(error => {
            console.error('Failed to fetch group leader info:', error);
            container.innerHTML = `<p class="text-red-600">Failed to load groups. Please try again later.</p>`;
        });
}
