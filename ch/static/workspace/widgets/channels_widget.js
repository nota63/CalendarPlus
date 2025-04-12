// Fetch and render workspace channels 
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
          <div class="mb-3 p-2 rounded bg-gray-50 border">
            <div class="d-flex align-items-center mb-1">
              ${msg.user.profile_picture ? `<img src="${msg.user.profile_picture}" class="rounded-circle me-2" style="width: 30px; height: 30px;">` : ""}
              <strong>${msg.user.full_name || msg.user.username}</strong>
              <span class="ms-auto text-muted text-sm">${msg.timestamp}</span>
            </div>
            <div>${msg.content || ""}</div>
            ${msg.replies.length ? msg.replies.map(reply => `
              <div class="ms-4 mt-2 p-2 bg-white border rounded-sm">
                <small><strong>${reply.user.full_name || reply.user.username}</strong>: ${reply.content}</small>
              </div>`).join('') : ''}
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
  