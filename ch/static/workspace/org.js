
// Refresh and keep the time
document.addEventListener("DOMContentLoaded", function () {
    const refreshBtn = document.getElementById("refresh-btn");
    const refreshIcon = document.getElementById("refresh-icon");
    const lastRefreshed = document.getElementById("last-refreshed");

    // Load last refreshed time from localStorage (if exists)
    const savedTime = localStorage.getItem("lastRefreshed");
    if (savedTime) {
        lastRefreshed.textContent = `Last refreshed: ${savedTime}`;
    }

    refreshBtn.addEventListener("click", function () {
        // Add rotation animation
        refreshIcon.classList.add("animate-spin");

        // Simulate refresh delay
        setTimeout(() => {
            refreshIcon.classList.remove("animate-spin");

            // Get current time and update localStorage
            const now = new Date();
            const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            
            localStorage.setItem("lastRefreshed", timeString);
            lastRefreshed.textContent = `Last refreshed: ${timeString}`;
        }, 800); // 800ms smooth effect
    });
});


// Preview and manage installed apps
document.addEventListener("DOMContentLoaded", function () {
    const openAppsModalBtn = document.getElementById("openAppsModal");
    const appsContainer = document.getElementById("appsContainer");

    openAppsModalBtn.addEventListener("click", function () {
        const orgId = window.djangoData.orgId;  // Assuming orgId is available globally

        if (!orgId) {
            console.error("Organization ID is missing.");
            return;
        }

        // Clear previous data
        appsContainer.innerHTML = `<p class="text-gray-500">Loading apps...</p>`;

        // Fetch installed apps
        fetch(`/apps/fetch-installed-apps/${orgId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    appsContainer.innerHTML = `<p class="text-red-500">${data.error}</p>`;
                    return;
                }

                appsContainer.innerHTML = ""; // Clear loading message

                if (data.installed_apps.length === 0) {
                    appsContainer.innerHTML = `<p class="text-gray-500">No apps installed.</p>`;
                    return;
                }

                data.installed_apps.forEach(app => {
                    const appElement = document.createElement("a");
                    appElement.href = `/apps/launch_app/${orgId}/${app.id}/`;  // Redirect on click
                    appElement.classList.add("block", "group", "flex", "items-center", "gap-3", "p-2", "border", "rounded-lg", "bg-white", "shadow", "hover:bg-gray-100", "transition");

                    const appIcon = app.icon
                        ? `<img src="${app.icon}" alt="${app.name}" class="w-10 h-10 rounded-full object-cover">`
                        : `<div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500">📦</div>`;

                    appElement.innerHTML = `
                        ${appIcon}
                        <div class="flex-1">
                            <h3 class="text-sm font-medium text-gray-800 group-hover:text-blue-600">${app.name}</h3>
                            <p class="text-xs text-gray-500">Version: ${app.version}</p>
                        </div>
                    `;

                    appsContainer.appendChild(appElement);
                });
            })
            .catch(error => {
                console.error("Error fetching installed apps:", error);
                appsContainer.innerHTML = `<p class="text-red-500">Failed to load apps.</p>`;
            });
    });
});
