
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
                    ? `<img src="${app.icon}" alt="${app.name}" class="w-10 h-10 rounded-full object-cover">`
                    : `<div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500">📦</div>`;
                
                appLink.innerHTML = `
                    ${appIcon}
                    <div class="flex-1">
                        <h3 class="text-sm font-medium text-gray-800 group-hover:text-blue-600">${app.name}</h3>
                        <p class="text-xs text-gray-500">Version: ${app.version}</p>
                    </div>
                `;
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


// Create Channel (Admin Only)

// Create Channel (Admin Only)
document.addEventListener("DOMContentLoaded", function () {
    const visibilityOptions = document.querySelectorAll("input[name='visibility']");
    const visibilityHiddenInput = document.getElementById("visibility");
    const membersContainer = document.getElementById("membersContainer");
    const allowedMembersContainer = document.getElementById("allowedMembers");
    const channelForm = document.getElementById("channelForm");
    const channelTypeInput = document.getElementById("channelType");

    // Handle Channel Type Selection
    document.querySelectorAll(".channel-type").forEach(el => {
        el.addEventListener("click", function () {
            if (!this.classList.contains("pro")) {
                document.querySelectorAll(".channel-type").forEach(el => el.classList.remove("selected"));
                this.classList.add("selected");
                channelTypeInput.value = this.getAttribute("data-value");
            }
        });
    });

    // Handle Visibility Change
      // Handle Visibility Change (Radio Buttons)
      visibilityOptions.forEach(option => {
        option.addEventListener("change", function () {
            visibilityHiddenInput.value = this.value; // Update hidden input

            if (this.value === "PRIVATE") {
                membersContainer.classList.remove("d-none");
                fetchMembers();
            } else {
                membersContainer.classList.add("d-none");
            }
        });
    });
    function fetchMembers() {
        const orgId = window.djangoData.orgId;

        fetch(`/organizations/fetch-org-members-updated/${orgId}/`)
            .then(response => response.json())
            .then(data => {
                allowedMembersContainer.innerHTML = "";
                data.members.forEach(member => {
                    let memberCard = document.createElement("div");
                    memberCard.classList.add("member-card");
                    memberCard.setAttribute("data-id", member.id);

                    memberCard.innerHTML = `
                    <div class="flex items-center space-x-4 p-2 hover:bg-gray-50 rounded-lg transition-colors duration-200 group">
                      <div class="relative">
                        <img 
                          src="${member.profile_picture}" 
                          alt="${member.name}" 
                          class="w-10 h-10 rounded-full object-cover border-2 border-white shadow-sm"
                        >
                        <!-- Online status indicator -->
                        <span class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></span>
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-900 truncate">
                          ${member.full_name}
                        </p>
                        <p class="text-xs text-gray-500 truncate">
                          ${member.role} • Last active 2h ago
                        </p>
                      </div>
                      <div class="flex items-center space-x-2">
                        <button class="p-1.5 hover:bg-gray-100 rounded-full transition-colors">
                          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                  `;

                    memberCard.addEventListener("click", function () {
                        this.classList.toggle("selected");
                    });

                    allowedMembersContainer.appendChild(memberCard);
                });
            })
            .catch(error => console.error("Error fetching members:", error));
    }

    channelForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const orgId = window.djangoData.orgId;
        const channelName = document.getElementById("channelName").value;
        const channelType = document.getElementById("channelType").value;
        const visibility = document.getElementById("visibility").value;
        const allowedMembers = Array.from(allowedMembersContainer.querySelectorAll(".member-card.selected"))
            .map(el => el.getAttribute("data-id"));

        if (visibility === "PRIVATE" && allowedMembers.length === 0) {
            alert("Please select allowed members for a Private channel.");
            return;
        }

        fetch(`/organizations/create-channel-updated/${orgId}/`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
            body: JSON.stringify({
                name: channelName,
                type: channelType,
                visibility: visibility,
                allowed_members: allowedMembers
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Channel created successfully!");
                location.reload();
            } else {
                alert("Error creating channel: " + data.message);
            }
        })
        .catch(error => console.error("Error:", error));
    });

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1];
    }
});

// Delete Channels (Bulk Action)
// Delete Channels (Bulk Action)
document.addEventListener("DOMContentLoaded", function () {
    const shutdownBtn = document.querySelector("#shutdownBtn"); // Trigger button
    const deleteChannelsModalEl = document.getElementById("deleteChannelsModal");
    const confirmDeleteModalEl = document.getElementById("confirmDeleteModal");

    const deleteChannelsModal = new bootstrap.Modal(deleteChannelsModalEl);
    const confirmDeleteModal = new bootstrap.Modal(confirmDeleteModalEl);

    const channelsContainer = document.getElementById("channelsContainer");
    const selectedChannelsContainer = document.getElementById("selectedChannelsList");
    const nextBtn = document.getElementById("nextStep");
    const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
    const passwordInput = document.getElementById("deletePasswordd");

    let selectedChannels = [];

    /** Open Delete Channels Modal */
    shutdownBtn.addEventListener("click", function (e) {
        e.preventDefault();
        deleteChannelsModal.show();
        fetchChannels();
    });

    /** Fetch Channels from Backend */
    function fetchChannels() {
        const orgId = window.djangoData.orgId;

        fetch(`/organizations/fetch-channels-updated/${orgId}/`)
            .then(response => response.json())
            .then(data => {
                channelsContainer.innerHTML = "";

                if (data.channels.length === 0) {
                    channelsContainer.innerHTML = `<p class="text-gray-500 text-sm">No channels available.</p>`;
                    return;
                }

                data.channels.forEach(channel => {
                    let channelItem = document.createElement("div");
                    channelItem.classList.add("channel-item", "flex", "items-center", "justify-between", "p-2", "hover:bg-gray-50", "rounded-md", "cursor-pointer");
                    channelItem.setAttribute("data-id", channel.id);

                    channelItem.innerHTML = `
                    <label class="group block cursor-pointer">
                        <input 
                            type="checkbox" 
                            class="channel-checkbox peer hidden" 
                            data-id="${channel.id}"
                        >
                        <div class="flex items-center justify-between p-3 rounded-lg transition-all duration-200
                                  border border-transparent 
                                  hover:border-gray-200 hover:bg-gray-50
                                  peer-checked:border-indigo-200 peer-checked:bg-indigo-50
                                  peer-checked:hover:bg-indigo-100 peer-focus-visible:ring-2 peer-focus-visible:ring-indigo-200">
                            
                            <div class="flex items-center space-x-3">
                                <!-- Channel icon with selection state -->
                                <div class="w-5 h-5 rounded bg-gradient-to-br from-blue-400 to-indigo-600
                                           peer-checked:from-indigo-600 peer-checked:to-indigo-700"></div>
                                <!-- Channel name with selection color -->
                                <span class="text-sm font-medium text-gray-700 truncate max-w-[200px]
                                            peer-checked:text-indigo-800">${channel.name}</span>
                            </div>
                
                            <!-- Enhanced checkbox with animated checkmark -->
                            <div class="relative flex items-center">
                                <div class="w-5 h-5 border-2 border-gray-300 rounded-md bg-white transition-all 
                                          flex items-center justify-center
                                          peer-checked:border-indigo-600 peer-checked:bg-indigo-600
                                          peer-checked:[&>svg]:animate-check">
                                    <svg class="hidden w-3 h-3 text-white stroke-current" 
                                         viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                                        <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round"/>
                                    </svg>
                                </div>
                            </div>
                        </div>
                    </label>
                `;                    channelsContainer.appendChild(channelItem);
                });
            })
            .catch(error => {
                console.error("Error fetching channels:", error);
                channelsContainer.innerHTML = `<p class="text-red-500 text-sm">Failed to load channels. Please try again.</p>`;
            });
    }

    /** Event Delegation: Handle Channel Selection */
    channelsContainer.addEventListener("click", function (event) {
        let target = event.target;

        if (target.classList.contains("channel-item") || target.tagName === "SPAN") {
            let checkbox = target.closest(".channel-item").querySelector(".channel-checkbox");
            checkbox.checked = !checkbox.checked;
            updateSelectedChannels();
        } else if (target.classList.contains("channel-checkbox")) {
            updateSelectedChannels();
        }
    });

    /** Update Selected Channels List */
    function updateSelectedChannels() {
        selectedChannels = Array.from(document.querySelectorAll(".channel-checkbox:checked"))
            .map(cb => cb.getAttribute("data-id"));

        nextBtn.disabled = selectedChannels.length === 0;
    }

    /** Open Password Confirmation Modal */
    nextBtn.addEventListener("click", function () {
        deleteChannelsModal.hide();

        selectedChannelsContainer.innerHTML = selectedChannels.length
            ? selectedChannels.map(id => `<li class="text-gray-900">${document.querySelector(`[data-id="${id}"] span`).innerText}</li>`).join("")
            : `<p class="text-gray-500 text-sm">No channels selected.</p>`;

        confirmDeleteModal.show();
    });

    /** Confirm Deletion with Password */
    confirmDeleteBtn.addEventListener("click", function () {
        const password = passwordInput.value.trim();
        if (!password) {
            alert("Please enter your password.");
            return;
        }
        console.log("Selected channels:", selectedChannels); // Debug here 💡

        confirmDeleteBtn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Deleting...`;
        confirmDeleteBtn.disabled = true;

        const orgId = window.djangoData.orgId;

        fetch(`/organizations/delete-channels-updated/${orgId}/`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
            body: JSON.stringify({ channel_ids: selectedChannels, password: password })

        })
        .then(response => response.json())
        .then(data => {
            confirmDeleteBtn.innerHTML = "Delete Channels";
            confirmDeleteBtn.disabled = false;

            if (data.success) {
                alert("Channels deleted successfully!");
                location.reload();
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch(error => {
            console.error("Error deleting channels:", error);
            confirmDeleteBtn.innerHTML = "Delete Channels";
            confirmDeleteBtn.disabled = false;
        });
    });

    /** Get CSRF Token */
    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1];
    }
});
