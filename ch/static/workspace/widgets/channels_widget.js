// Fetch and render workspace channels 
async function fetchAndRenderChannels(orgId) {
    const container = document.getElementById('channels-list-container');
    container.innerHTML = `
      <div class="flex items-center justify-center p-6 text-sm text-gray-500">
        <svg class="animate-spin h-5 w-5 mr-2 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Loading channels...
      </div>`;
    
    try {
      const response = await fetch(`/channels_widget/get-channels-widget/${orgId}/`);
      const data = await response.json();
      
      if (data.status !== "success" || !data.channels.length) {
        container.innerHTML = `
          <div class="flex flex-col items-center justify-center p-8 text-sm text-gray-400">
            <svg class="h-12 w-12 text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>No channels available.</p>
          </div>`;
        return;
      }
      
      container.innerHTML = `
        <div class="flex items-center justify-between mb-4 px-3">
          <h3 class="font-medium text-sm text-gray-700">All Channels</h3>
          <span class="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded-full">${data.channels.length}</span>
        </div>
        <div class="channels-list-wrapper overflow-y-auto max-h-96 pr-1">
          ${data.channels.map(channel => {
            // Determine channel type icon
            let typeIcon = '';
            switch(channel.type.toLowerCase()) {
              case 'text':
                typeIcon = '<svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20"><path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4z"></path><path fill-rule="evenodd" d="M3 8a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>';
                break;
              case 'voice':
                typeIcon = '<svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd"></path></svg>';
                break;
              default:
                typeIcon = '<svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"></path></svg>';
            }
            
            // Determine visibility badge
            let visibilityBadge = '';
            switch(channel.visibility.toLowerCase()) {
              case 'public':
                visibilityBadge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">Public</span>';
                break;
              case 'private':
                visibilityBadge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">Private</span>';
                break;
              default:
                visibilityBadge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">' + channel.visibility + '</span>';
            }
            
            return `
              <div class="channel-card bg-white border-l-4 border-l-indigo-500 border-t border-r border-b border-gray-200 rounded-r-lg shadow-sm p-3 hover:bg-gray-50 transition-all mb-2 cursor-pointer flex flex-col"
                  data-channel-id="${channel.id}">
                <div class="flex justify-between items-center mb-2">
                  <div class="flex items-center">
                    <span class="text-gray-900 font-medium text-sm">${channel.name}</span>
                    <span class="ml-2 text-xs text-gray-400 font-mono">#${channel.id}</span>
                  </div>
                  <div class="flex space-x-1">
                    <button class="text-gray-400 hover:text-indigo-600 transition-colors p-1 rounded-full hover:bg-indigo-50">
                      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
                      </svg>
                    </button>
                  </div>
                </div>
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-2 text-xs text-gray-500">
                    <div class="flex items-center space-x-1">
                      ${typeIcon}
                      <span>${channel.type}</span>
                    </div>
                    <div class="hidden sm:block">•</div>
                    <div class="hidden sm:block">${visibilityBadge}</div>
                  </div>
                  <div class="text-xs text-gray-400 flex items-center">
                    <span class="hidden sm:inline">Created by</span>
                    <span class="font-medium text-gray-600 ml-1">${channel.created_by}</span>
                    <span class="hidden md:inline ml-1 whitespace-nowrap">${channel.created_at}</span>
                  </div>
                </div>
              </div>`;
          }).join("")}
        </div>
        <div class="mt-4 px-3">
          <button class="w-full bg-indigo-50 hover:bg-indigo-100 text-indigo-600 text-sm font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center">
            <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Create Channel
          </button>
        </div>`;
        
      // Add hover effects after rendering
      document.querySelectorAll('.channel-card').forEach(card => {
        card.addEventListener('mouseover', () => {
          card.classList.add('shadow-md');
        });
        card.addEventListener('mouseout', () => {
          card.classList.remove('shadow-md');
        });
      });
      
    } catch (error) {
      console.error("Error fetching channels:", error);
      container.innerHTML = `
        <div class="text-red-500 text-sm p-4 bg-red-50 rounded-lg flex items-center">
          <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Failed to load channels. Please try again later.
        </div>`;
    }
  }

  // Channel card click handler
  document.body.addEventListener("click", async function (e) {
    const channelCard = e.target.closest(".channel-card");
    if (!channelCard) return;
  
    const channelId = channelCard.dataset.channelId;
    const orgId = window.currentOrgId;
  
    // Update modal title
    const modalTitle = document.getElementById("channelMessagesModalLabel");
    modalTitle.textContent = `#${channelId} Messages`;
  
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById("channelMessagesModal"));
    modal.show();
  
    // Fetch and render messages
    await fetchAndRenderChannelMessages(orgId, channelId);
  
    // Store active channel globally
    window.activeChannel = { channelId, orgId };
  });
  
// Handle sending a channel message
document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.getElementById("channel-message-textarea");
  
    if (!textarea) {
      console.error("[DEBUG] #channel-message-textarea not found!");
      return;
    }
  
    textarea.addEventListener("keydown", async function (event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();  // Prevent newline
  
        const text = textarea.value.trim();
        const audioFile = document.getElementById("channel-audio-input").files[0];
        const videoFile = document.getElementById("channel-video-input").files[0];
  
        console.log("[DEBUG] Text:", text);
        console.log("[DEBUG] Audio File:", audioFile);
        console.log("[DEBUG] Video File:", videoFile);
  
        if (!text && !audioFile && !videoFile) {
          alert("Please enter a message or attach media.");
          return;
        }
  
        const formData = new FormData();
        formData.append("content", text);
        if (audioFile) formData.append("audio", audioFile);
        if (videoFile) formData.append("video", videoFile);
  
        const channelId = window.activeChannel?.channelId;
        const orgId = window.activeChannel?.orgId;
  
        if (!channelId || !orgId) {
          alert("Cannot send message. Channel not active.");
          return;
        }
  
        try {
          const response = await fetch(`/channels_widget/send-channel-message/${channelId}/`, {
            method: "POST",
            headers: {
              "X-CSRFToken": getCSRFToken(),
            },
            body: formData,
          });
  
          const data = await response.json();
          console.log("[DEBUG] Server response:", data);
  
          if (data.status === "success") {
            textarea.value = "";
            document.getElementById("channel-audio-input").value = "";
            document.getElementById("channel-video-input").value = "";
            fetchAndRenderChannelMessages(orgId, channelId);
          } else {
            alert("Failed to send message: " + (data.message || "Unknown error"));
          }
        } catch (error) {
          console.error("[DEBUG] Error:", error);
          alert("Error sending message.");
        }
      }
    });
  });
  
  
// Fetch messages and render them
  // Fetch messages and render them
  async function fetchAndRenderChannelMessages(orgId, channelId) {
    const container = document.getElementById("channel-messages-container");
    container.innerHTML = `<div class="text-sm text-gray-500">Loading messages...</div>`;
  
    try {
      const res = await fetch(`/channels_widget/get-channel-messages/${window.djangoData.orgId}/${channelId}/`);
      const data = await res.json();
  
      if (!data.messages.length) {
        container.innerHTML = `<div class="text-sm text-gray-400">No messages yet.</div>`;
        return;
      }
  
      container.innerHTML = data.messages.map(msg => {
        return `
  <div class="mb-4 p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow transition-shadow">
    <div class="flex items-start gap-3">
      <div class="flex items-center mb-2">
        ${msg.user.profile_picture ? `
          <img src="${msg.user.profile_picture}" 
               class="w-8 h-8 rounded-full object-cover mr-3 border-2 border-white shadow-sm">
        ` : ''}
        <div class="flex flex-col">
          <span class="text-sm font-semibold text-gray-700">${msg.user.full_name || msg.user.username}</span>
          <span class="text-xs text-gray-400">${msg.timestamp}</span>
        </div>
      </div>
    </div>

    <div class="pl-11">
      <p class="text-gray-700 text-sm leading-relaxed mb-3">${msg.content || ""}</p>
      
      ${msg.replies.length ? `
        <div class="space-y-2 border-l-2 border-gray-100 pl-4">
          ${msg.replies.map(reply => `
            <div class="flex items-start pt-2">
              ${reply.user.profile_picture ? `
                <img src="${reply.user.profile_picture}" 
                     class="w-6 h-6 rounded-full mr-2 mt-1 border-2 border-white shadow-sm">
              ` : ''}
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-xs font-semibold text-gray-700">${reply.user.full_name || reply.user.username}</span>
                  <span class="text-xs text-gray-400">${reply.timestamp}</span>
                </div>
                <p class="text-gray-600 text-sm leading-snug">${reply.content}</p>
              </div>
            </div>
          `).join('')}
        </div>
      ` : ''}
    </div>
  </div>
`;
      }).join("");
    } catch (error) {
      console.error("Error fetching messages:", error);
      container.innerHTML = `<div class="text-sm text-red-500">Failed to load messages.</div>`;
    }
  }
  
  // CSRF token getter for Django
  function getCSRFToken() {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='));
    return cookieValue ? cookieValue.split('=')[1] : '';
  }
  