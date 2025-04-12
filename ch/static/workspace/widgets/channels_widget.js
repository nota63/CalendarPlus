
// Fetch and render workspace channels 
async function fetchAndRenderChannels(orgId) {
    const container = document.getElementById('channels-list-container');
    container.innerHTML = `<div class="text-sm text-gray-500">Loading channels...</div>`;
  
    try {
      const response = await fetch(`/channels_widget/get-channels-widget/${orgId}/`);
      const data = await response.json();
  
      if (data.status !== "success" || !data.channels.length) {
        container.innerHTML = `<div class="text-sm text-gray-400">No channels available.</div>`;
        return;
      }
  
      const channelHTML = data.channels.map(channel => {
        return `
          <div class="channel-card bg-white border border-gray-200 rounded-lg shadow-sm p-3 hover:shadow-md transition-all mb-3 cursor-pointer" 
               data-channel-id="${channel.id}">
            <div class="flex justify-between items-center mb-1">
              <span class="text-indigo-600 font-semibold text-sm">${channel.name}</span>
              <span class="text-xs text-gray-400">#${channel.id}</span>
            </div>
            <div class="text-xs text-gray-500 mb-1">
              <strong>Type:</strong> ${channel.type} &bull; <strong>Visibility:</strong> ${channel.visibility}
            </div>
            <div class="text-xs text-gray-400">
              Created by <span class="font-medium text-gray-600">${channel.created_by}</span> on ${channel.created_at}
            </div>
          </div>
        `;
      }).join("");
  
      container.innerHTML = channelHTML;
  
    } catch (error) {
      console.error("Error fetching channels:", error);
      container.innerHTML = `<div class="text-red-500 text-sm">Failed to load channels.</div>`;
    }
  }
  