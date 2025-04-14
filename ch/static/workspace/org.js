
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



// RAISE HELP REQUEST --- USER-Impersonation System
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('helpRequestForm');
    const msg = document.getElementById('helpResponseMsg');
    const modalElement = document.getElementById('raiseHelpModal');
    const bootstrapModal = bootstrap.Modal.getOrCreateInstance(modalElement);
  
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      msg.textContent = '';
      msg.classList.remove('text-danger', 'text-success');
  
      const orgId =window.djangoData.orgId; // Set this properly in template context
      const formData = new FormData(form);
  
      try {
        const response = await fetch(`/subscription/raise-help-request-live/${orgId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
          body: formData,
        });
  
        const data = await response.json();
        console.log("📨 Ajax Response:", data);
  
        if (data.success) {
          msg.textContent = data.message;
          msg.classList.add('text-success');
          form.reset();
  
          setTimeout(() => {
            bootstrapModal.hide();
            msg.textContent = '';
          }, 1500);
        } else {
          msg.textContent = data.message || 'Failed to raise request.';
          msg.classList.add('text-danger');
        }
      } catch (err) {
        console.error("❌ Ajax Error:", err);
        msg.textContent = 'Something went wrong. Try again.';
        msg.classList.add('text-danger');
      }
    });
  
    function getCSRFToken() {
      const token = document.querySelector('[name=csrfmiddlewaretoken]');
      if (token) return token.value;
  
      const name = 'csrftoken';
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          return decodeURIComponent(cookie.substring(name.length + 1));
        }
      }
      return '';
    }
  });


// Fetch users help requests and tickets
// Wait until DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("MyHelpRequestsModal");
  
    if (modal) {
      modal.addEventListener("show.bs.modal", () => {
        const orgId = window.djangoData?.orgId;
  
        if (!orgId) {
          console.error("Organization ID not found.");
          return;
        }
  
        fetchAndRenderHelpRequests(orgId);
      });
    }
  });
  
  // Fetch help requests via Ajax
  async function fetchAndRenderHelpRequests(orgId) {
    const container = document.getElementById("helpRequestsContainer");
    if (!container) return;
  
    container.innerHTML = `<div class="text-muted">Loading help requests...</div>`;
  
    try {
      const response = await fetch(`/subscription/fetch-my-help-requests/${orgId}/`, {
        method: "GET",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });
  
      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }
  
      const data = await response.json();
  
      if (data.success) {
        renderHelpRequests(data.requests, container);
      } else {
        container.innerHTML = `<div class="text-danger">Failed to load help requests. Try again later.</div>`;
      }
  
    } catch (error) {
      console.error("Error fetching help requests:", error);
      container.innerHTML = `<div class="text-danger">Something went wrong while fetching data.</div>`;
    }
  }
  
  // Render help request cards
  function renderHelpRequests(requests, container) {
    container.innerHTML = "";
  
    if (!Array.isArray(requests) || requests.length === 0) {
      container.innerHTML = `<div class="text-muted">No help requests found.</div>`;
      return;
    }
  
    requests.forEach((req) => {
      const card = document.createElement("div");

      card.className = "col-12 mb-3";
  
      card.innerHTML = `
  <div class="border-l-4 border-${getStatusColor(req.status)} bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
    <div class="p-5 space-y-3">
      <h3 class="text-gray-800 font-semibold text-lg leading-tight">${escapeHtml(req.title)}</h3>
      
      <p class="text-gray-600 text-sm leading-relaxed">${escapeHtml(req.description)}</p>

      <div class="flex items-center gap-2">
        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-${getStatusColor(req.status)}-100 text-${getStatusColor(req.status)}-800">
          ${req.status.toUpperCase()}
        </span>
        <span class="text-gray-400 text-xs">•</span>
        <span class="text-gray-500 text-sm">${req.created_at}</span>
      </div>

      <div class="flex flex-wrap gap-2 pt-2">
        ${req.attachment_url 
          ? `<a href="${req.attachment_url}" class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500" target="_blank" rel="noopener noreferrer">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              View Attachment
            </a>` 
          : ""
        }

        <button class="inline-flex items-center px-4 py-2 border border-gray-800 rounded-lg text-sm font-medium text-gray-800 hover:bg-gray-800 hover:text-white transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500" 
          data-bs-toggle="modal" 
          data-bs-target="#ImpersonationActivitiesModal"
          onclick="fetchImpersonationLogs('${req.uuid}')">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
          View Logs
        </button>
      </div>
    </div>
  </div>
`;
      container.appendChild(card);
    });
  }
  
  // Convert status to Bootstrap color class
  function getStatusColor(status) {
    switch ((status || "").toLowerCase()) {
      case "initiated": return "warning";
      case "pending": return "secondary";
      case "solved": return "success";
      default: return "dark";
    }
  }
  // Escape HTML to prevent injection
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
  
// Fetch impersonation logs for a help request
 // Safe HTML escape helper
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
  
  // Main function to fetch impersonation logs
  async function fetchImpersonationLogs(helpRequestId) {
    const logContainer = document.getElementById("impersonationLogContainer");
  
    if (!logContainer) {
      console.error("🚫 Log container not found in DOM");
      return;
    }
  
    logContainer.innerHTML = `<div class="text-muted p-3">Loading activity logs...</div>`;
  
    try {
      const response = await fetch(`/subscription/fetch-impersonation-logs/${helpRequestId}/`, {
        method: "GET",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });
  
      const text = await response.text();
      console.log("🧾 Raw response:", text);
  
      let data;
      try {
        data = JSON.parse(text);
      } catch (jsonError) {
        console.error("❌ Failed to parse JSON:", jsonError);
        logContainer.innerHTML = `<div class="text-danger p-3">Invalid server response format.</div>`;
        return;
      }
  
      // Fallback logic: support both `data.success === true` or `data.status === 'success'`
      const isSuccess = data.success === true || data.status === 'success';
  
      if (!isSuccess) {
        console.warn("⚠️ Response status not marked as success:", data);
        logContainer.innerHTML = `<div class="text-danger p-3">Failed to fetch logs from the server.</div>`;
        return;
      }
  
      const logs = data.logs;
  
      if (!Array.isArray(logs) || logs.length === 0) {
        logContainer.innerHTML = `<div class="text-muted p-3">No activities found for this help request.</div>`;
        return;
      }
  
      // Render logs
      logContainer.innerHTML = logs.map((log, index) => {
        const adminInitial = log.admin ? escapeHtml(log.admin.charAt(0).toUpperCase()) : 'N/A';
        const methodColors = {
          GET: 'bg-green-500',
          POST: 'bg-blue-500',
          PUT: 'bg-yellow-500',
          DELETE: 'bg-red-500',
          PATCH: 'bg-purple-500',
          default: 'bg-gray-500'
        };
        const methodColor = methodColors[log.method.toUpperCase()] || methodColors.default;
      
        return `
          <div class="flex group relative">
            <!-- Timeline line -->
            <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 ${index === 0 ? 'top-6' : ''} ${index === logs.length - 1 ? 'h-6' : ''}"></div>
            
            <!-- Left avatar/icon column -->
            <div class="relative z-10 flex-shrink-0 w-8 mr-4">
              <div class="absolute left-0 top-6 h-6 w-6 ${methodColor} rounded-full flex items-center justify-center text-white font-semibold shadow-sm">
                ${adminInitial}
              </div>
            </div>
      
            <!-- Right content card -->
            <div class="flex-1 pb-8">
              <div class="relative bg-white rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-all duration-200 p-4">
                <!-- Header -->
                <div class="flex items-start justify-between mb-2">
                  <div>
                    <h3 class="font-semibold text-gray-900">${escapeHtml(log.admin || 'N/A')}</h3>
                    <p class="text-sm text-gray-500 mt-1">${escapeHtml(log.organization || 'N/A')}</p>
                  </div>
                  <span class="text-sm text-gray-500 whitespace-nowrap">${escapeHtml(log.timestamp)}</span>
                </div>
      
                <!-- Method and path -->
                <div class="flex items-center gap-2 mb-3">
                  <span class="${methodColor} text-white px-2 py-1 rounded-full text-xs font-medium">${escapeHtml(log.method)}</span>
                  <code class="text-sm font-mono text-gray-700">${escapeHtml(log.path)}</code>
                </div>
      
                <!-- User Agent -->
                <div class="mt-3">
                  <p class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">User Agent</p>
                  <div class="bg-gray-50 p-2 rounded-lg text-sm font-mono text-gray-600 break-words">
                    ${escapeHtml(log.user_agent || 'N/A')}
                  </div>
                </div>
      
                <!-- Data -->
                <div class="mt-3">
                  <p class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Data</p>
                  <pre class="bg-gray-50 p-2 rounded-lg text-sm font-mono text-gray-600 overflow-x-auto">${JSON.stringify(log.request_data || {}, null, 2)}</pre>
                </div>
      
                <!-- Decorative corner icon -->
                <svg class="absolute top-4 right-4 h-5 w-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                </svg>
              </div>
            </div>
          </div>
        `;
      }).join('');


  
    } catch (error) {
      console.error("❌ Network or server error:", error);
      logContainer.innerHTML = `<div class="text-danger p-3">Something went wrong while fetching logs. Please try again later.</div>`;
    }
  }
  

// Fetch and display help requests of the organization
// 🌟 Help Request Loader for Admin Modal
document.addEventListener("DOMContentLoaded", () => {
    const helpModal = document.getElementById('OrgHelpRequestReviewModal');

    if (!helpModal) {
        console.warn("[HelpReviewModal] Modal element missing.");
        return;
    }

    helpModal.addEventListener('show.bs.modal', () => {
        const orgId = window?.djangoData?.orgId;

        if (!orgId) {
            console.error("[HelpReviewModal] orgId missing in window.djangoData.");
            return;
        }

        console.info(`[HelpReviewModal] Triggered for org ID: ${orgId}`);
        fetchOrgHelpRequests(orgId);
    });
});

async function fetchOrgHelpRequests(orgId) {
    const displayContainer = document.getElementById('orgHelpRequestsListContainer');

    if (!displayContainer) {
        console.warn("[HelpReviewModal] Container not found in DOM.");
        return;
    }

    displayContainer.innerHTML = `<p class="text-muted">Fetching help requests...</p>`;

    try {
        const response = await fetch(`/subscription/fetch-all-help-requests/${orgId}/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            throw new Error(`[HelpReviewModal] Server returned ${response.status}`);
        }

        const result = await response.json();
        console.debug("[HelpReviewModal] Fetched response:", result);

        if (!result.success) {
            displayContainer.innerHTML = `<p class="text-danger">${result.error || 'Failed to fetch help requests.'}</p>`;
            return;
        }

        renderOrgHelpRequests(result.requests);
    } catch (err) {
        console.error("[HelpReviewModal] Fetch error:", err);
        displayContainer.innerHTML = `<p class="text-danger">Something went wrong while fetching help requests.</p>`;
    }
}

function renderOrgHelpRequests(requests) {
    const container = document.getElementById('orgHelpRequestsListContainer');
    container.innerHTML = '';

    if (!Array.isArray(requests) || requests.length === 0) {
        container.innerHTML = `<p class="text-muted">No help requests found for this organization.</p>`;
        return;
    }

    for (const req of requests) {
        const wrapper = document.createElement('div');

        wrapper.className = 'w-full mb-4';

        wrapper.innerHTML = `
        <div class="bg-white rounded-lg border border-gray-200 shadow-xs hover:shadow-md transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] hover:-translate-y-0.5 group">
          <div class="p-4 flex items-center justify-between gap-3">
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <div class="relative flex-shrink-0">
                <img src="${req.profile_picture || '/static/img/default-avatar.png'}"
                     class="rounded-full w-9 h-9 object-cover ring-2 ring-gray-100"
                     alt="User avatar">
                <div class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-white"></div>
              </div>
              
              <div class="flex-1 min-w-0 space-y-0.5">
                <h6 class="font-semibold text-gray-900 text-[15px] leading-tight truncate">
                  ${sanitizeText(req.title)}
                </h6>
                <div class="flex items-center gap-2 text-gray-500">
                  <span class="text-xs font-medium truncate">${sanitizeText(req.user_full_name)}</span>
                  <div class="w-1 h-1 bg-gray-300 rounded-full"></div>
                  <span class="flex items-center gap-1 text-xs font-medium text-purple-600">
                    <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z"/>
                      <path d="M10 12.5a1 1 0 01-1-1V8a1 1 0 112 0v3.5a1 1 0 01-1 1zm0 1.5a1 1 0 100 2 1 1 0 000-2z"/>
                    </svg>
                    Active
                  </span>
                </div>
              </div>
            </div>
        
            <button class="p-2 -m-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors duration-150"
                    data-bs-toggle="modal"
                    data-bs-target="#HelpRequestFullDetailModal"
                    data-request-id="${req.uuid}">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </button>
          </div>
        </div>
        `;
        container.appendChild(wrapper);
    }

    // Attach click listeners for each View button
    setTimeout(() => {
        document.querySelectorAll('[data-request-id]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const uuid = e.currentTarget.getAttribute('data-request-id');
                if (uuid) {
                    fetchHelpRequestDetail(uuid);
                }
            });
        });
    }, 0);
}

// 💥 Fetch full help request details by UUID
async function fetchHelpRequestDetail(uuid) {
    const modalBody = document.getElementById('helpRequestDetailBody');
    modalBody.innerHTML = `<p class="text-muted">Loading request details...</p>`;

    try {
        const res = await fetch(`/subscription/get-help-request-detail/${uuid}/`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        const data = await res.json();

        if (!data.success || !data.data) {
            console.error("[HelpRequestDetail] Invalid or missing data object:", data);
            modalBody.innerHTML = `<p class="text-danger">${data.error || 'Failed to fetch help request details.'}</p>`;
            return;
        }

        const detail = data.data;

        modalBody.innerHTML = `
        <div class="space-y-4">
          <div class="flex items-center justify-between pb-2 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-900">
              ${sanitizeText(detail.title || 'Untitled Request')}
            </h3>
            <span class="px-2.5 py-1 rounded-full text-xs font-medium ${detail.status === 'Resolved' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}">
              ${sanitizeText(detail.status || 'N/A')}
            </span>
          </div>
        
          <div class="grid grid-cols-3 gap-4 text-sm">
            <div class="space-y-1">
              <label class="text-gray-500 font-medium">Requester</label>
              <div class="flex items-center gap-2">
                <img src="${detail.profile_picture || '/static/img/default-avatar.png'}" 
                     class="w-6 h-6 rounded-full object-cover">
                <span class="text-gray-900">${sanitizeText(detail.username || 'Unknown user')}</span>
              </div>
            </div>
        
            <div class="space-y-1">
              <label class="text-gray-500 font-medium">Created</label>
              <p class="text-gray-900">${detail.created_at || 'N/A'}</p>
            </div>
        
            <div class="space-y-1">
              <label class="text-gray-500 font-medium">Priority</label>
              <p class="flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full ${detail.priority === 'high' ? 'bg-red-500' : 'bg-gray-300'}"></span>
                <span class="text-gray-900 capitalize">${detail.priority || 'normal'}</span>
              </p>
            </div>
          </div>
        
          <div class="space-y-2">
            <label class="text-gray-500 font-medium text-sm">Description</label>
            <div class="p-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-700 text-sm">
              ${sanitizeText(detail.description || 'No description provided')}
            </div>
          </div>
        
          ${detail.attachment ? `
          <div class="space-y-2">
            <label class="text-gray-500 font-medium text-sm">Attachment</label>
            <a href="${detail.attachment}" target="_blank" 
               class="group flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800">
              <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <span class="truncate">${detail.attachment.split('/').pop()}</span>
            </a>
          </div>` : ''}
        
          <div class="pt-4 border-t border-gray-200 flex justify-end gap-2">
            <a href="/subscription/login-as-user/${window.djangoData.orgId}/${detail.uuid}/${detail.help_user_id}/" 
               class="inline-flex items-center px-3.5 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/>
              </svg>
              Start Session
            </a>
          </div>
        </div>
        `;


    } catch (err) {
        console.error("[HelpRequestDetail] Fetch failed:", err);
        modalBody.innerHTML = `<p class="text-danger">Something went wrong while loading request details.</p>`;
    }
}

// 🚨 Output sanitization to prevent injection
function sanitizeText(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}


// --------------------------------------------------------------------------------------------------------------------------------------------------------
// Users widgets (Re-order (Drag and drop))
function enableWidgetDragAndSave() {
  const container = document.getElementById("dashboard-widgets-container");

  const waitForWidgets = setInterval(() => {
    if (container.children.length > 0) {
      clearInterval(waitForWidgets);

      const savedOrder = JSON.parse(localStorage.getItem("dashboard_widget_order"));
      if (savedOrder && Array.isArray(savedOrder)) {
        savedOrder.forEach(id => {
          const el = document.getElementById(id);
          if (el) container.appendChild(el);
        });
      }

      new Sortable(container, {
        animation: 200,
        ghostClass: 'drag-ghost',
        chosenClass: 'drag-chosen',
        dragClass: 'drag-moving',
        onEnd: function () {
          const order = Array.from(container.children).map(child => child.id);
          localStorage.setItem("dashboard_widget_order", JSON.stringify(order));
          console.log("✅ Widget order saved:", order);
        }
      });

      console.log("🎯 Drag and drop with style enabled");
    }
  }, 300);
}

document.addEventListener("DOMContentLoaded", enableWidgetDragAndSave);

// ----------------------------------------------------------------------------------------------------------------------------------------------
// 🧩 Main Dashboard Widgets JS
document.addEventListener('DOMContentLoaded', function () {
  const widgetButtons = document.querySelectorAll('.add-widget-btn');
  const modalEl = document.getElementById('widgetSelectModal');
  const widgetsContainer = document.getElementById('dashboard-widgets-container');
  const orgId = window.djangoData.orgId;  // Make sure this is passed in via template context

  function getCSRFToken() {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))?.split('=')[1];
    return cookieValue || '{{ csrf_token }}';  // fallback for safety
  }

  // ✨ Centralized initializer
  function initializeWidget(widgetType) {
    switch (widgetType) {
      case 'group-widget':
        console.log("⚙️ Running group widget init JS...");
        fetchAndRenderUserGroups(orgId);
        break;
      case 'calculation-widget':
        console.log("⚙️ Running calculation widget init JS...");
        fetchAndRenderCalculationWidget(orgId);
        break;
      case 'workload-widget':
        console.log("⚙️ Running workload widget init JS...");
        fetchAndRenderUnifiedPieChart(orgId);
        break;
      case 'progress-widget':
        console.log("⚙️ Running progress widget init JS...");
        fetchAndRenderProgress(orgId);
        break;
      case 'overdue-tasks-widget':
        console.log("⚙️ Running overdue tasks widget init JS...");
        fetchAndRenderOverdueTasks(orgId);
        break;
      case 'due-soon-tasks-widget':
        console.log("⚙️ Running due soon tasks widget init JS...");
        fetchAndRenderDueSoonTasks(orgId);
        break;
      //bookmarks widget
      case 'bookmarks-widget':
        fetchAndRenderBookmarks(orgId);
        break;
      case 'resources-widget':
        console.log('resources widget initialized')
        fetchAndRenderResources(orgId);
        break;
      case 'recent-activity-widget':
        console.log('recent activity widget initialized')
        fetchAndRenderRecentActivity(orgId);
        break;
      case 'channels-widget':
        console.log('channels widget initialized')
        fetchAndRenderChannels(orgId);
        break;
      case 'time-traced-widget':
        console.log('time traced widget initialized')
        fetchTimeTracing(orgId);
        break;
      case 'balance-widget':
          console.log('balance widget initialized')
          fetchCalPoints(orgId);
          break;
      case 'high-priority-tasks-widget':
          console.log('high priority tasks widget initialized')
          fetchHighPriorityTasks(orgId);
          break; 
      case 'google-docs-widget':
            console.log('Google docs widget initialized')
            fetchGoogleDocEmbed();
            break; 
      case 'google-sheets-widget':
              console.log('Google sheets widget initialized')
              fetchGoogleSheetEmbed();
              break;
      case 'youtube-widget':
              console.log('youtube video embed widget initialized')
              fetchYouTubeEmbed();
              break;
      case 'figma-widget':
              console.log('figma prototype embed widget initialized')
              fetchFigmaEmbed();
              break;
      case 'tasks-in-progress-widget':
              console.log('tasks in progress widget initialized')
              fetchTasksProgressCount(orgId);
              break;
      case 'completed-tasks-widget':
              FetchCompletedTasksSummary(orgId);
              break;
      case 'status-over-time-widget':
              FetchStatusOverTime(orgId);
              break;
      case 'tag-usage-widget':
              FetchTagUsageSummary(orgId);
              break;            
                                                       
      default:
        console.warn("❓ No init logic defined for widget type:", widgetType);
    }
  }

  // 🔁 Load all widgets on initial page load
  function loadAllWidgetsOnPageLoad() {
    console.log("🌐 Loading saved widgets...");
    fetch(`/dashboard/all-widget-snippets/?org_id=${orgId}`)
      .then(response => {
        if (!response.ok) throw new Error("Failed to fetch all widgets");
        return response.text();
      })
      .then(html => {
        widgetsContainer.innerHTML = html;
        console.log("✅ All widgets rendered.");

        // 🧠 Initialize widgets by detecting their presence
        const widgetMap = {
          '#group-list': 'group-widget',
          '#calculation-widget': 'calculation-widget',
          '#workload-chart-widget': 'workload-widget',
          '#progress-widget': 'progress-widget',
          '#overdue-tasks-widget': 'overdue-tasks-widget',
          '#due-soon-tasks-widget': 'due-soon-tasks-widget',
          '#bookmarks-widget': 'bookmarks-widget',
          '#resources-widget':'resources-widget',
          '#recent-activity-widget':'recent-activity-widget',
          '#channels-widget':'channels-widget',
          '#time-traced-widget':'time-traced-widget',
          '#high-priority-tasks-widget':'high-priority-tasks-widget',
          '#balance-widget':'balance-widget',
          '#google-docs-widget':'google-docs-widget',
          '#google-sheets-widget':'google-sheets-widget',
          '#youtube-widget':'youtube-widget',
          '#figma-widget':'figma-widget',
          '#tasks-in-progress-widget':'tasks-in-progress-widget',
          '#completed-tasks-widget':'completed-tasks-widget',
          '#status-over-time-widget':'status-over-time-widget',
          '#tag-usage-widget':'tag-usage-widget',
        };

        Object.entries(widgetMap).forEach(([selector, widgetType]) => {
          if (widgetsContainer.querySelector(selector)) {
            console.log(`🔍 Detected ${selector} — initializing ${widgetType}...`);
            initializeWidget(widgetType);
          }
        });
      })
      .catch(error => {
        console.error("💥 Error loading widgets:", error);
      });
  }


// ➕ Handle "Add Widget" button click
widgetButtons.forEach(btn => {
  btn.addEventListener('click', function () {
    const widgetType = this.getAttribute('data-widget');
    const csrfToken = getCSRFToken();

    console.log("👉 Saving widget:", widgetType);
    console.log("📡 Sending to org_id:", orgId);

    fetch('/dashboard/save-widget/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({
        widget_type: widgetType,
        org_id: orgId
      })
    })
      .then(response => {
        console.log("✅ Response status:", response.status);
        return response.json();
      })
      .then(data => {
        console.log("📦 Response data:", data);
        if (data.message) {
          alert(data.message);

          // 👇 Fetch and render the widget immediately after saving
          fetch(`/dashboard/widget-snippet/?widget_type=${widgetType}&org_id=${orgId}`)
            .then(res => res.text())
            .then(html => {
              widgetsContainer.insertAdjacentHTML('beforeend', html);
              console.log("🧩 Widget rendered successfully:", widgetType);

              // ✅ Initialize it dynamically now
              initializeWidget(widgetType);
            })
            .catch(err => {
              console.error("❌ Failed to render widget snippet:", err);
            });

          // ✨ Close modal and cleanup backdrop/blur
          if (bootstrap && modalEl) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal?.hide();

            // ⛑️ Fix: Remove leftover modal-backdrop and blur class
            document.body.classList.remove('modal-open');
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
          }

        } else if (data.error) {
          alert('❌ Error: ' + data.error);
          console.error("❌ Backend error:", data.error);
        }
      })
      .catch(error => {
        console.error('💥 Request failed:', error);
        alert('Something went wrong while saving the widget.');
      });
  });
});

loadAllWidgetsOnPageLoad();  // 🔁 Initial call
});
