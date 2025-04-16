function HandleAndFetchChat(orgId) {
    fetch(`/discussion_widget/fetch-chat-users/${orgId}/`)
      .then(response => response.json())
      .then(data => {
        const container = document.getElementById('discussion-widget');
        container.innerHTML = '';
  
        data.users.forEach(user => {
          const userDiv = document.createElement('div');
          userDiv.className = 'd-flex align-items-center mb-2 chat-user';
          userDiv.setAttribute('data-user-id', user.user_id);
          userDiv.innerHTML = `
          <div class="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors duration-150 cursor-pointer">
            <div class="relative flex-shrink-0">
              <img 
                src="${user.profile_picture || '/static/default-avatar.png'}" 
                class="w-8 h-8 rounded-full object-cover border border-gray-200 dark:border-gray-700"
                alt="${user.full_name}'s avatar"
              >
              ${user.status === 'online' ? 
                '<span class="absolute bottom-0 right-0 block w-2 h-2 bg-green-500 rounded-full ring-1 ring-white dark:ring-gray-800"></span>' : 
                ''
              }
            </div>
            <div class="ml-3 flex flex-col">
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">${user.full_name}</span>
              ${user.title ? 
                `<span class="text-xs text-gray-500 dark:text-gray-400">${user.title}</span>` : 
                ''
              }
            </div>
            ${user.unread_notifications ? 
              `<div class="ml-auto">
                <span class="inline-flex items-center justify-center w-5 h-5 text-xs font-medium text-white bg-indigo-600 rounded-full">
                  ${user.unread_notifications > 9 ? '9+' : user.unread_notifications}
                </span>
              </div>` : 
              ''
            }
          </div>
        `;
          userDiv.addEventListener('click', () => openChatModal(user.user_id, user.full_name, orgId));
          container.appendChild(userDiv);
        });
      })
      .catch(err => console.error("Error loading users:", err));
  }
  
  function openChatModal(userId, userName, orgId) {
    const modal = new bootstrap.Modal(document.getElementById('chatModal'));
    document.getElementById('chatModalLabel').innerText = `Chat with ${userName}`;
    document.getElementById('chatUserId').value = userId;
    document.getElementById('chatOrgId').value = orgId;
    document.getElementById('chatMessages').innerHTML = '';
    modal.show();
  
    fetch(`/discussion_widget/handle-chat/?receiver_id=${userId}&org_id=${orgId}`)
      .then(res => res.json())
      .then(data => {
        const chatBox = document.getElementById('chatMessages');
        data.messages.forEach(msg => {
          const bubble = document.createElement('div');

          // Enhanced chat bubble with Tailwind CSS styling for ClickUp-like UI
bubble.className = msg.sender === CURRENT_USER_ID 
? 'flex flex-col items-end mb-4 max-w-3/4 ml-auto' 
: 'flex flex-col items-start mb-4 max-w-3/4';

// Create avatar element with first letter of sender
const avatar = document.createElement('div');
const senderInitial = (msg.sender.toString()[0] || '?').toUpperCase();
avatar.className = msg.sender === CURRENT_USER_ID
? 'w-8 h-8 rounded-full flex items-center justify-center text-white bg-indigo-600 text-sm font-medium ml-2 order-2'
: 'w-8 h-8 rounded-full flex items-center justify-center text-white bg-gray-500 text-sm font-medium mr-2 order-1';
avatar.textContent = senderInitial;

// Create message content container
const messageContent = document.createElement('div');
messageContent.className = msg.sender === CURRENT_USER_ID
? 'order-1 mr-2 py-2 px-4 bg-indigo-100 rounded-2xl rounded-tr-none shadow-sm text-indigo-900'
: 'order-2 ml-2 py-2 px-4 bg-gray-100 rounded-2xl rounded-tl-none shadow-sm text-gray-900';

// Add message text with proper styling
const messageText = document.createElement('div');
messageText.className = 'text-sm font-normal break-words';
messageText.textContent = msg.text;

// Add timestamp with subtle styling
const timestamp = document.createElement('div');
timestamp.className = 'text-xs text-gray-500 mt-1';
timestamp.textContent = msg.timestamp;

// Append text and timestamp to message content
messageContent.appendChild(messageText);
messageContent.appendChild(timestamp);

// Clear and rebuild the bubble with new structure
bubble.innerHTML = '';
bubble.className += ' flex items-start';
bubble.appendChild(avatar);
bubble.appendChild(messageContent);
          chatBox.appendChild(bubble);
        });
      });
  }
  
  function sendMessage() {
    const userId = document.getElementById('chatUserId').value;
    const orgId = document.getElementById('chatOrgId').value;
    const text = document.getElementById('chatInput').value;
    const file = document.getElementById('chatFile').files[0];
    const code = document.getElementById('chatCode').value;
  
    if (!text.trim() && !file && !code.trim()) return;
  
    const formData = new FormData();
    formData.append('receiver_id', userId);
    formData.append('org_id', orgId);
    formData.append('text', text);
    formData.append('code_snippet', code);
    if (file) formData.append('file', file);
  
    fetch('/discussion_widget/handle-chat/', {
      method: 'POST',
      body: formData,
      headers: { 'X-CSRFToken': getCSRFToken() }
    })
      .then(res => res.json())
      .then(data => {
        const chatBox = document.getElementById('chatMessages');
        const bubble = document.createElement('div');
        bubble.className = 'text-end text-primary';
  
        let content = '<div class="flex flex-col space-y-2">';

        // Message text with proper styling
        if (text) {
          content += `<div class="text-sm text-gray-800 leading-relaxed break-words">${text}</div>`;
        }
        
        // Code snippet with improved styling
        if (code) {
          content += `
            <div class="relative bg-gray-100 rounded-md p-3 border-l-4 border-indigo-500">
              <div class="absolute top-2 right-2 text-xs px-2 py-1 bg-gray-200 rounded text-gray-600 font-medium">CODE</div>
              <pre class="text-xs font-mono text-gray-800 whitespace-pre-wrap overflow-x-auto mt-2 max-h-60 scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100"><code>${code}</code></pre>
            </div>
          `;
        }
        
        // File attachment with icon and better visual
        if (data.file_url) {
          content += `
            <a href="${data.file_url}" target="_blank" class="flex items-center space-x-2 text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 transition duration-200 py-2 px-3 rounded-md w-fit">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
              </svg>
              <span class="text-sm font-medium">Download File</span>
            </a>
          `;
        }
        
        // Timestamp with subtle styling
        content += `<div class="text-xs text-gray-400 mt-1">${data.timestamp}</div>`;
        content += '</div>';
        
        bubble.innerHTML = content;
        chatBox.appendChild(bubble);
  
        document.getElementById('chatInput').value = '';
        document.getElementById('chatCode').value = '';
        document.getElementById('chatFile').value = '';
      });
  }
  
  
  function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  }
  

// save code 
function toggleCodeInput() {
    const codeInput = document.getElementById("chatCode");
    codeInput.style.display = codeInput.style.display === "none" ? "block" : "none";
  }

 
// # Widget 2)Total time traced----------------------------------------------------------------------------------------------------------------

function FetchTotalTimeBatteryChart(orgId) {
  const loading = document.getElementById("timeWidgetLoading");
  const container = document.getElementById("batteryChartContainer");

  // Clear existing content + show loader
  container.innerHTML = "";
  loading.classList.remove("hidden");

  fetch(`/discussion_widget/time-spent-battery-chart/${window.djangoData.orgId}/`)
    .then(response => response.json())
    .then(data => {
      loading.classList.add("hidden");

      if (data.status === 'success') {
        if (data.data.length === 0) {
          container.innerHTML = "<p class='text-sm text-gray-500'>No data found.</p>";
        } else {
          data.data.forEach(item => {
            const batteryColor = item.battery_level >= 75
              ? 'bg-green-500'
              : item.battery_level >= 40
              ? 'bg-yellow-400'
              : 'bg-red-500';

            const userBar = `
              <div class="space-y-1">
                <div class="flex justify-between text-sm text-gray-700 font-medium">
                  <span>${item.user}</span>
                  <span>${item.time_hours.toFixed(2)} hrs</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-3">
                  <div class="${batteryColor} h-3 rounded-full" style="width: ${item.battery_level}%"></div>
                </div>
              </div>
            `;
            container.insertAdjacentHTML('beforeend', userBar);
          });
        }
      } else {
        container.innerHTML = `<p class="text-red-600 text-sm">${data.message}</p>`;
      }
    })
    .catch(error => {
      loading.classList.add("hidden");
      console.error("Time battery chart fetch failed:", error);
      container.innerHTML = `<p class="text-red-600 text-sm">Something went wrong fetching time data.</p>`;
    });
}
