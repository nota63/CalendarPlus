
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
    const uninstallAppBtn = document.createElement("button");
    let selectedAppId = null;
    let selectedOrgId = window.djangoData.orgId;

    // Create custom modal dynamically
    const customModal = document.createElement("div");
    customModal.id = "customUninstallModal";
    customModal.className = "fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 hidden";
    customModal.innerHTML = `
        <div class="bg-white p-5 rounded-lg shadow-lg w-96">
            <img id="appIcon" class="w-12 h-12 rounded-full object-cover mb-3 hidden" alt="App Icon">
            <h2 class="text-lg font-semibold mb-2" id="appName"></h2>
            <p class="text-gray-700 text-sm mb-4" id="appDescription"></p>
            <p class="text-gray-600 text-xs" id="appVersion"></p>
            <p class="text-gray-600 text-xs" id="appDeveloper"></p>
            <p class="text-gray-600 text-xs" id="appCategory"></p>
            <div class="flex justify-end mt-4">
                <button id="cancelUninstall" class="mr-2 px-4 py-2 text-gray-700 bg-gray-200 rounded">Cancel</button>
                <button id="confirmUninstall" class="px-4 py-2 bg-red-500 text-white rounded">Uninstall</button>
            </div>
        </div>
    `;
    document.body.appendChild(customModal);

    const confirmUninstallBtn = document.getElementById("confirmUninstall");
    const cancelUninstallBtn = document.getElementById("cancelUninstall");

    openAppsModalBtn.addEventListener("click", function () {
        if (!selectedOrgId) {
            console.error("Organization ID is missing.");
            return;
        }

        appsContainer.innerHTML = `<p class="text-gray-500">Loading apps...</p>`;

        fetch(`/apps/fetch-installed-apps/${selectedOrgId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    appsContainer.innerHTML = `<p class="text-red-500">${data.error}</p>`;
                    return;
                }

                appsContainer.innerHTML = "";

                if (data.installed_apps.length === 0) {
                    appsContainer.innerHTML = `<p class="text-gray-500">No apps installed.</p>`;
                    return;
                }

                data.installed_apps.forEach(app => {
                    const appElement = document.createElement("div");
                    appElement.classList.add("relative", "group", "flex", "items-center", "gap-3", "p-2", "border", "rounded-lg", "bg-white", "shadow", "hover:bg-gray-100", "transition");
                    
                    const appLink = document.createElement("a");
                    appLink.href = `/apps/launch_app/${selectedOrgId}/${app.id}/`;
                    appLink.classList.add("block", "group", "flex", "items-center", "gap-3", "w-full");
                    
                    const appIcon = app.icon
  ? `<img src="${app.icon}" alt="${app.name}" class="w-12 h-12 rounded-xl border border-gray-100 shadow-sm object-cover transition-transform duration-200 group-hover:scale-105">`
  : `<div class="w-12 h-12 rounded-xl bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center text-2xl shadow-sm">📦</div>`;

appLink.innerHTML = `
  <div class="flex items-start gap-4 w-full">
    ${appIcon}
    <div class="flex-1 space-y-1.5">
      <div class="flex items-baseline justify-between gap-2">
        <h3 class="text-base font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">${app.name}</h3>
        <span class="text-xs font-medium px-1.5 py-1 rounded bg-green-100 text-green-800">${app.version}</span>
      </div>
      ${app.description ? `<p class="text-sm text-gray-600 line-clamp-2">${app.description}</p>` : ''}
      <div class="flex items-center gap-2 text-xs text-gray-500">
        <span class="flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          ${app.category || 'General'}
        </span>
      </div>
    </div>
  </div>
`;

appLink.className = `
  group block p-4 bg-white rounded-xl border border-gray-200
  hover:border-blue-200 hover:shadow-lg transition-all duration-200
  ease-in-out hover:transform hover:-translate-y-0.5
`;

appElement.className = "w-full md:w-1/2 xl:w-1/3 p-2"; // For grid layout container
appElement.appendChild(appLink);
                    
                    const uninstallButton = document.createElement("button");
                    uninstallButton.className = "absolute top-2 right-2 hidden group-hover:block bg-red-500 text-white px-2 py-1 text-xs rounded hover:bg-red-600 transition";
                    uninstallButton.textContent = "Uninstall";
                    uninstallButton.dataset.appId = app.id;
                    
                    uninstallButton.addEventListener("click", function (event) {
                        event.stopPropagation();
                        event.preventDefault();
                        selectedAppId = app.id;

                        fetch(`/apps/miniapp-details/${selectedOrgId}/${selectedAppId}/`)
                            .then(response => response.json())
                            .then(data => {
                                if (data.error) {
                                    console.error("Error fetching app details:", data.error);
                                    return;
                                }

                                document.getElementById("appName").textContent = data.app_details.name;
                                document.getElementById("appDescription").textContent = data.app_details.description;
                                document.getElementById("appVersion").textContent = `Version: ${data.app_details.version}`;
                                document.getElementById("appDeveloper").textContent = `Developer: ${data.app_details.developer}`;
                                document.getElementById("appCategory").textContent = `Category: ${data.app_details.category}`;
                                
                                const appIconElement = document.getElementById("appIcon");
                                if (data.app_details.icon) {
                                    appIconElement.src = data.app_details.icon;
                                    appIconElement.classList.remove("hidden");
                                } else {
                                    appIconElement.classList.add("hidden");
                                }

                                customModal.classList.remove("hidden");
                            })
                            .catch(error => {
                                console.error("Error fetching app details:", error);
                            });
                    });

                    appElement.appendChild(uninstallButton);
                    appsContainer.appendChild(appElement);
                });
            })
            .catch(error => {
                console.error("Error fetching installed apps:", error);
                appsContainer.innerHTML = `<p class="text-red-500">Failed to load apps.</p>`;
            });
    });

    confirmUninstallBtn.addEventListener("click", function () {
        if (!selectedAppId || !selectedOrgId) {
            console.error("Missing app or org ID.");
            return;
        }

        fetch(`/apps/uninstall/${selectedOrgId}/${selectedAppId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("App uninstalled successfully!");
                customModal.classList.add("hidden");
                openAppsModalBtn.click();
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => {
            console.error("Error uninstalling app:", error);
        });
    });

    cancelUninstallBtn.addEventListener("click", function () {
        customModal.classList.add("hidden");
    });

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }
});
