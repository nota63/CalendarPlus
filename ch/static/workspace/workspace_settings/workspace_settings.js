// Handle workspace creation
document.getElementById('createOrgBtn').addEventListener('click', function () {
    const existingModal = document.getElementById('createOrgModal');
    if (existingModal) existingModal.remove(); // prevent duplicates

    const modalHTML = `
    <div id="createOrgModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 overflow-y-auto">
      <div class="relative w-full max-w-3xl mx-auto my-6 md:my-8">
        <div class="relative flex flex-col w-full bg-white rounded-lg shadow-xl border border-gray-100 overflow-hidden">
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <h5 class="text-lg font-semibold text-gray-800">Create Organization & Invite Members</h5>
            <button type="button" class="text-gray-400 hover:text-gray-600 focus:outline-none" data-bs-dismiss="modal" aria-label="Close">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
              </svg>
            </button>
          </div>
          
          <!-- Body -->
          <div class="p-6 space-y-4 max-h-[70vh] overflow-y-auto custom-scrollbar">
            <form id="orgInviteForm" class="space-y-4">
              <!-- Organization Details -->
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Organization Name</label>
                  <input type="text" name="name" required class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm" placeholder="Enter organization name">
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea name="description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm" placeholder="Brief description of your organization"></textarea>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select name="status" class="w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm">
                    <option value="working_remotely">Working Remotely</option>
                    <option value="in_office">In Office</option>
                    <option value="hybrid">Hybrid</option>
                  </select>
                </div>
              </div>
              
              <!-- Divider -->
              <div class="border-t border-gray-200 my-4"></div>
              
              <!-- Invite Members -->
              <div id="invitesWrapper" class="space-y-3">
                <div class="flex items-center justify-between">
                  <h6 class="text-sm font-medium text-gray-700">Invite Members</h6>
                  <button type="button" id="addInviteBtn" class="flex items-center text-sm text-blue-600 hover:text-blue-800">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                    </svg>
                    Add Member
                  </button>
                </div>
                
                <div class="invite-field flex flex-wrap md:flex-nowrap items-center gap-2">
                  <input type="email" class="w-full md:flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm" placeholder="Email address" required>
                  <select class="w-full md:w-32 px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm" required>
                    <option value="manager">Manager</option>
                    <option value="employee">Employee</option>
                  </select>
                  <button type="button" class="remove-invite flex items-center justify-center w-8 h-8 rounded-md bg-red-50 hover:bg-red-100 text-red-500">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                  </button>
                </div>
              </div>
            </form>
          </div>
          
          <!-- Footer -->
          <div class="flex items-center justify-end px-6 py-4 bg-gray-50 border-t border-gray-100 gap-3">
            <button type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" form="orgInviteForm" class="flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              <span>Create & Invite</span>
            </button>
          </div>
          
          <!-- Loading Overlay -->
          <div id="loadingOverlay" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80 hidden">
            <div class="flex flex-col items-center">
              <div class="w-12 h-12 rounded-full border-4 border-blue-100 border-t-blue-600 animate-spin"></div>
              <p class="mt-3 text-sm text-gray-600">Creating workspace...</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Add custom scrollbar styles
    const styleElement = document.createElement('style');
    styleElement.textContent = `
      .custom-scrollbar::-webkit-scrollbar {
        width: 4px;
      }
      .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
      }
      .custom-scrollbar::-webkit-scrollbar-thumb {
        background-color: rgba(156, 163, 175, 0.3);
        border-radius: 20px;
      }
      .custom-scrollbar {
        scrollbar-width: thin;
        scrollbar-color: rgba(156, 163, 175, 0.3) transparent;
      }
    `;
    document.head.appendChild(styleElement);

    // Add dynamic invite field logic
    document.getElementById('addInviteBtn').addEventListener('click', () => {
      const field = `
        <div class="invite-field flex flex-wrap md:flex-nowrap items-center gap-2 animate-fadeIn">
          <input type="email" class="w-full md:flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm" placeholder="Email address" required>
          <select class="w-full md:w-32 px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm" required>
            <option value="manager">Manager</option>
            <option value="employee">Employee</option>
          </select>
          <button type="button" class="remove-invite flex items-center justify-center w-8 h-8 rounded-md bg-red-50 hover:bg-red-100 text-red-500">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
          </button>
        </div>`;
      document.getElementById('invitesWrapper').insertAdjacentHTML('beforeend', field);
    });

    // Remove invite field
    document.addEventListener('click', function (e) {
      if (e.target.classList.contains('remove-invite') || e.target.closest('.remove-invite')) {
        const inviteField = e.target.closest('.invite-field');
        inviteField.classList.add('opacity-0');
        setTimeout(() => {
          inviteField.remove();
        }, 200);
      }
    });

    // Close modal on backdrop click and escape key
    const modal = document.getElementById('createOrgModal');
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeModal();
      }
    });
    
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && modal) {
        closeModal();
      }
    });
    
    function closeModal() {
      modal.classList.add('opacity-0');
      setTimeout(() => {
        modal.remove();
      }, 200);
    }
    
    // Find close button and attach event
    const closeBtn = modal.querySelector('[data-bs-dismiss="modal"]');
    if (closeBtn) {
      closeBtn.addEventListener('click', closeModal);
    }

    // Form submit AJAX with loading spinner
    document.getElementById('orgInviteForm').addEventListener('submit', function (e) {
      e.preventDefault();

      const form = e.target;
      const loadingOverlay = document.getElementById('loadingOverlay');
      
      // Show loading spinner
      loadingOverlay.classList.remove('hidden');

      const name = form.querySelector('input[name="name"]').value;
      const description = form.querySelector('textarea[name="description"]').value;
      const status = form.querySelector('select[name="status"]').value;

      const inviteFields = form.querySelectorAll('.invite-field');
      const invitations = [];

      inviteFields.forEach(field => {
        const email = field.querySelector('input').value;
        const role = field.querySelector('select').value;
        invitations.push({ email, role });
      });

      fetch("/workspace_settings/create-workspace/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),  // Replace with your method
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          name,
          description,
          status,
          invitations
        })
      })
      .then(res => res.json())
      .then(data => {
        // Hide loading spinner
        loadingOverlay.classList.add('hidden');
        
        if (data.success) {
          // Show success notification
          // 🧡 Redirect to org detail page
    window.location.href = data.redirect_url;
} else {
  alert("Error: " + (data.error || "Something went wrong!"));
}
      })
      .catch(err => {
        console.error(err);
        loadingOverlay.classList.add('hidden');
        showNotification("AJAX error occurred", 'error');
      });
    });

    // Notification function
    function showNotification(message, type = 'success') {
      const existingNotification = document.getElementById('notification');
      if (existingNotification) existingNotification.remove();
      
      const bgColor = type === 'success' ? 'bg-green-50 border-green-500 text-green-800' : 'bg-red-50 border-red-500 text-red-800';
      const iconColor = type === 'success' ? 'text-green-400' : 'text-red-400';
      
      const notificationHTML = `
      <div id="notification" class="fixed top-4 right-4 flex items-center p-4 rounded-lg shadow-lg border-l-4 ${bgColor} transition-all duration-300 translate-x-full">
        <div class="${iconColor} flex-shrink-0 mr-3">
          ${type === 'success' 
            ? '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>'
            : '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>'
          }
        </div>
        <p class="text-sm font-medium">${message}</p>
        <button class="ml-auto text-gray-400 hover:text-gray-600">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </button>
      </div>
      `;
      
      document.body.insertAdjacentHTML('beforeend', notificationHTML);
      const notification = document.getElementById('notification');
      
      // Animate in
      setTimeout(() => {
        notification.classList.remove('translate-x-full');
      }, 10);
      
      // Auto dismiss
      setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
      }, 5000);
      
      // Close button
      notification.querySelector('button').addEventListener('click', () => {
        notification.classList.add('translate-x-full');
        setTimeout(() => notification.remove(), 300);
      });
    }

    // Show modal with animation
    setTimeout(() => {
      const modal = document.getElementById('createOrgModal');
      modal.classList.add('opacity-100');
      modal.classList.add('animate-fadeIn');
    }, 10);
});