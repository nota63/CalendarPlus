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
            <img src="${user.profile_picture || '/static/default-avatar.png'}" class="rounded-circle me-2" width="32" height="32">
            <strong>${user.full_name}</strong>
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
          bubble.className = msg.sender === CURRENT_USER_ID ? 'text-end text-primary' : 'text-start text-secondary';
          bubble.innerHTML = `<small>${msg.text}</small><br><small class="text-muted">${msg.timestamp}</small>`;
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
  
        let content = '';
        if (text) content += `<small>${text}</small><br>`;
        if (code) content += `<pre class="bg-light p-2 rounded"><code>${code}</code></pre>`;
        if (data.file_url) content += `<a href="${data.file_url}" target="_blank">Download File</a><br>`;
  
        content += `<small class="text-muted">${data.timestamp}</small>`;
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
  