// CSRF helper   
function getCSRFToken() {     
    return document.cookie.split('; ')       
      .find(row => row.startsWith('csrftoken='))       
      ?.split('=')[1];   
  }    
  
  // Fetch and display the bookmarks   
  async function fetchAndRenderBookmarks(orgId) {     
    const widgetContainer = document.getElementById('bookmarks-content');     
    widgetContainer.innerHTML = `<div class="flex items-center justify-center p-4 text-gray-500 text-sm">Loading bookmarks...</div>`;      
  
    try {       
      const response = await fetch(`/bookmarks/user-bookmarks/${orgId}/`, {         
        headers: {           
          'X-Requested-With': 'XMLHttpRequest',         
        },       
      });        
  
      if (!response.ok) {         
        throw new Error(`HTTP ${response.status}`);       
      }        
  
      const data = await response.json();        
  
      if (data.data.length === 0) {         
        widgetContainer.innerHTML = `<div class="text-gray-400 text-sm p-4">No bookmarks found yet 💭</div>`;         
        return;       
      }        
  
      // Render bookmarks       
      const bookmarksHTML = data.data.map((item, index) => {         
        return `           
          <div class="p-3 mb-2 border border-gray-200 rounded-lg bg-white hover:bg-gray-50 shadow-sm hover:shadow-md transition-all duration-200 group relative" id="bookmark-${index}">             
            <div class="flex justify-between items-center">               
              <a href="${item.url}" target="_blank" class="text-blue-600 font-medium hover:underline flex items-center">                 
                <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.172 13.828a4 4 0 005.656 0l4-4a4 4 0 10-5.656-5.656l-1.102 1.101"></path>
                </svg>
                ${item.title}               
              </a>               
              ${item.pinned ? '<span class="flex items-center text-amber-500 text-xs font-medium bg-amber-50 px-2 py-1 rounded-full"><svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v10a2 2 0 01-2 2H7a2 2 0 01-2-2V5z"></path></svg> Pinned</span>' : ''}             
            </div>             
            <p class="text-sm text-gray-600 mt-1">${item.description || ''}</p>              
            
            <!-- Delete button - PRESERVE ORIGINAL LOGIC -->             
            <button                
              class="position-absolute top-0 end-0 m-1 btn btn-sm btn-outline-danger d-none delete-btn bg-white hover:bg-red-50 text-red-500 border border-red-200 rounded text-xs px-2 py-1 absolute top-2 right-2"               
              data-id="${index}"               
              title="Delete"             
            >               
              <i class="bi bi-trash"></i>
              <svg class="w-3 h-3 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
                       
            </button>           
          </div>         
        `;       
      }).join('');        
  
      widgetContainer.innerHTML = bookmarksHTML;        
  
      // PRESERVE ORIGINAL HOVER LOGIC
      document.querySelectorAll('#bookmarks-content > div').forEach(bookmarkDiv => {         
        bookmarkDiv.addEventListener('mouseenter', () => {           
          bookmarkDiv.querySelector('.delete-btn').classList.remove('d-none');         
        });         
        bookmarkDiv.addEventListener('mouseleave', () => {           
          bookmarkDiv.querySelector('.delete-btn').classList.add('d-none');         
        });       
      });        
  
      // Add delete button events       
      document.querySelectorAll('.delete-btn').forEach(button => {         
        button.addEventListener('click', function () {           
          const bookmarkId = this.getAttribute('data-id');           
          deleteBookmark(orgId, bookmarkId);         
        });       
      });      
    } catch (error) {       
      console.error("Failed to fetch bookmarks:", error);       
      widgetContainer.innerHTML = `<div class="text-red-500 text-sm p-4 bg-red-50 rounded">Failed to load bookmarks. Try again later.</div>`;     
    }   
  }    
  
  // Delete bookmark   
  async function deleteBookmark(orgId, bookmarkId) {     
    if (!confirm("Are you sure you want to delete this bookmark?")) return;      
    
    try {       
      const res = await fetch(`/bookmarks/delete-bookmark/${orgId}/${bookmarkId}/`, {         
        method: 'POST',         
        headers: {           
          'Content-Type': 'application/json',           
          'X-CSRFToken': getCSRFToken(),         
        },       
      });        
      
      if (res.ok) {         
        document.getElementById(`bookmark-${bookmarkId}`)?.remove();       
      } else {         
        alert('Failed to delete the bookmark.');       
      }     
    } catch (err) {       
      console.error('Error deleting bookmark:', err);     
    }   
  }    
  
  // Call this on page load or widget load   
  document.addEventListener("DOMContentLoaded", function () {     
    const orgId = window.djangoData?.orgId;     
    if (orgId) {       
      fetchAndRenderBookmarks(orgId);     
    }   
  });

// Add bookmarks
 // ✅ CSRF Token helper
 function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
  }

  // ✅ Open Modal Function
  function openAddBookmarkModal() {
    const modalElement = document.getElementById('addBookmarkModal');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
  }

  // ✅ Submit Bookmark Function
  async function submitBookmark() {
    const title = document.getElementById('bookmarkTitle').value.trim();
    const url = document.getElementById('bookmarkURL').value.trim();
    const orgId = window.djangoData?.orgId;

    if (!title || !url) {
      alert("Please fill in both Title and URL.");
      return;
    }

    try {
      const response = await fetch(`/bookmarks/add-bookmark/${orgId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ title, url })
      });

      if (!response.ok) {
        throw new Error('Failed to add bookmark.');
      }

      // Hide modal & clear fields
      const modal = bootstrap.Modal.getInstance(document.getElementById('addBookmarkModal'));
      modal.hide();
      document.getElementById('bookmarkTitle').value = '';
      document.getElementById('bookmarkURL').value = '';

      // Optional: Refresh the bookmarks view
      fetchAndRenderBookmarks(orgId);

    } catch (error) {
      console.error(error);
      alert("Something went wrong while adding the bookmark.");
    }
  }

  // ✅ Optional: Hook a button to open the modal
  document.addEventListener('DOMContentLoaded', function () {
    const addButton = document.getElementById('openBookmarkModalBtn');
    if (addButton) {
      addButton.addEventListener('click', openAddBookmarkModal);
    }
  });


// Widget 2 ) - Resources Widget ----------------------------------------------------------------------------------------------------

// fetch and display the resources uploaded by the user across the workspace
// fetch and display the resources uploaded by the user across the workspace
async function fetchAndRenderResources(orgId) {
  const container = document.getElementById("resources-widget");
  container.innerHTML = `
    <div class="flex justify-center items-center p-6 min-h-20 bg-gray-50 rounded-lg border border-gray-100">
      <div class="flex items-center space-x-2">
        <svg class="animate-spin h-4 w-4 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-gray-500 font-medium text-sm">Loading your resources...</span>
      </div>
    </div>`;
    
  try {
    const response = await fetch(`/bookmarks/user-resources/${orgId}/`, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });
    
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const result = await response.json();
    
    if (result.data.length === 0) {
      container.innerHTML = `
        <div class="flex flex-col items-center justify-center p-8 bg-gray-50 rounded-lg border border-gray-100 text-center">
          <svg class="w-10 h-10 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
          </svg>
          <div class="text-gray-400 font-medium">No resources uploaded yet 💭</div>
          <p class="text-gray-400 text-xs mt-2">Upload files to see them here</p>
        </div>`;
      return;
    }
    
    const itemsHTML = result.data.map(item => {
      const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(item.file_name);
      const isPDF = /\.pdf$/i.test(item.file_name);
      const isDoc = /\.(doc|docx)$/i.test(item.file_name);
      const isExcel = /\.(xls|xlsx)$/i.test(item.file_name);
      
      let previewHTML = '';
      let iconBgClass = 'bg-blue-50';
      let iconTextClass = 'text-blue-500';
      
      if (isImage) {
        previewHTML = `<img src="${item.file_url}" alt="${item.file_name}" class="w-full h-full object-cover rounded">`;
      } else if (isPDF) {
        iconBgClass = 'bg-red-50';
        iconTextClass = 'text-red-500';
        previewHTML = `
          <div class="flex items-center justify-center w-full h-full ${iconBgClass} rounded">
            <svg class="w-8 h-8 ${iconTextClass}" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512">
              <path d="M320 464c8.8 0 16-7.2 16-16V160H256c-17.7 0-32-14.3-32-32V48H64c-8.8 0-16 7.2-16 16V448c0 8.8 7.2 16 16 16H320zM0 64C0 28.7 28.7 0 64 0H229.5c17 0 33.3 6.7 45.3 18.7l90.5 90.5c12 12 18.7 28.3 18.7 45.3V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64z"/>
            </svg>
          </div>`;
      } else if (isDoc) {
        iconBgClass = 'bg-blue-50';
        iconTextClass = 'text-blue-600';
        previewHTML = `
          <div class="flex items-center justify-center w-full h-full ${iconBgClass} rounded">
            <svg class="w-8 h-8 ${iconTextClass}" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512">
              <path d="M64 0C28.7 0 0 28.7 0 64V448c0 35.3 28.7 64 64 64H320c35.3 0 64-28.7 64-64V160H256c-17.7 0-32-14.3-32-32V0H64zM256 0V128H384L256 0zM112 256H272c8.8 0 16 7.2 16 16s-7.2 16-16 16H112c-8.8 0-16-7.2-16-16s7.2-16 16-16zm0 64H272c8.8 0 16 7.2 16 16s-7.2 16-16 16H112c-8.8 0-16-7.2-16-16s7.2-16 16-16zm0 64H272c8.8 0 16 7.2 16 16s-7.2 16-16 16H112c-8.8 0-16-7.2-16-16s7.2-16 16-16z"/>
            </svg>
          </div>`;
      } else if (isExcel) {
        iconBgClass = 'bg-green-50';
        iconTextClass = 'text-green-600';
        previewHTML = `
          <div class="flex items-center justify-center w-full h-full ${iconBgClass} rounded">
            <svg class="w-8 h-8 ${iconTextClass}" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512">
              <path d="M64 0C28.7 0 0 28.7 0 64V448c0 35.3 28.7 64 64 64H320c35.3 0 64-28.7 64-64V160H256c-17.7 0-32-14.3-32-32V0H64zM256 0V128H384L256 0zM155.7 250.2L192 302.1l36.3-51.9c7.6-10.9 22.6-13.5 33.4-5.9s13.5 22.6 5.9 33.4L221.3 344l46.4 66.2c7.6 10.9 5 25.8-5.9 33.4s-25.8 5-33.4-5.9L192 385.8l-36.3 51.9c-7.6 10.9-22.6 13.5-33.4 5.9s-13.5-22.6-5.9-33.4L162.7 344l-46.4-66.2c-7.6-10.9-5-25.8 5.9-33.4s25.8-5 33.4 5.9z"/>
            </svg>
          </div>`;
      } else {
        previewHTML = `
          <div class="flex items-center justify-center w-full h-full bg-gray-50 rounded">
            <svg class="w-8 h-8 text-gray-400" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512">
              <path d="M0 64C0 28.7 28.7 0 64 0H224V128c0 17.7 14.3 32 32 32H384V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zm384 64H256V0L384 128z"/>
            </svg>
          </div>`;
      }
      
      const fileType = item.type.replace('_', ' ').toUpperCase();
      const typeColorClass = 
        fileType.includes('IMAGE') ? 'bg-purple-100 text-purple-700' :
        fileType.includes('PDF') ? 'bg-red-100 text-red-700' :
        fileType.includes('DOC') ? 'bg-blue-100 text-blue-700' :
        fileType.includes('EXCEL') ? 'bg-green-100 text-green-700' :
        'bg-indigo-100 text-indigo-700';
      
        return `
        <div class="group flex flex-col bg-white rounded-md border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-all duration-200 hover:border-indigo-300">
          <a href="${item.file_url}" target="_blank" class="block h-36 overflow-hidden rounded-md">
            ${previewHTML}
          </a>
          <div class="p-3 flex flex-col flex-grow">
            <div class="flex items-center justify-between mb-2">
              <span class="px-2 py-1 text-xs font-medium rounded-full ${typeColorClass}">
                ${fileType}
              </span>
              <span class="text-xs text-gray-400">${item.uploaded_at || '—'}</span>
            </div>
            <p class="text-sm font-medium text-gray-700 line-clamp-2 mb-2" title="${item.file_name}">
              ${item.file_name}
            </p>
            <div class="mt-auto">
              <a href="${item.file_url}" target="_blank" class="inline-flex items-center text-xs font-medium text-indigo-600 hover:text-indigo-800 transition-colors">
                <span>View file</span>
                <svg class="ml-1 w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                </svg>
              </a>
            </div>
          </div>
        </div>
      `;
    }).join("");
    container.innerHTML = `
      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div class="flex justify-between items-center p-4 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-800">Resources</h2>
          <div class="flex space-x-2">
            <button class="p-2 text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
              </svg>
              Filter
            </button>
            <button class="p-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md transition-colors flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              Add New
            </button>
          </div>
        </div>
        
        <div class="p-4 max-h-96 overflow-y-auto">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            ${itemsHTML}
          </div>
        </div>
      </div>
    `;
  } catch (error) {
    console.error("Failed to load resources:", error);
    container.innerHTML = `
      <div class="flex flex-col items-center justify-center p-8 bg-white rounded-lg border border-gray-200 text-center">
        <div class="bg-red-100 p-3 rounded-full mb-3">
          <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-700 mb-1">Oops! Something went wrong</h3>
        <p class="text-gray-500 text-sm mb-4">Could not load your resources</p>
        <button onclick="fetchAndRenderResources('${orgId}')" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md transition-colors flex items-center">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          Try Again
        </button>
      </div>
    `;
  }
}


// Widget 3 ) Fetch recent activity (Recent activity widget)----------------------------------------------------------------------------------------------------------
const activityCache = {};

async function fetchAndRenderRecentActivity(orgId) {
  const container = document.getElementById('recent-activity-widget');
  container.innerHTML = `
    <div class="flex items-center justify-center py-6 text-slate-500">
      <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" fill="currentColor"></path>
      </svg>
      <span class="font-medium">Loading recent activities...</span>
    </div>`;
  
  try {
    const response = await fetch(`/bookmarks/fetch-recent-activity-methods/${orgId}/`);
    const data = await response.json();
    
    if (!data.activities || data.activities.length === 0) {
      container.innerHTML = `
        <div class="flex flex-col items-center justify-center py-10 text-slate-400">
          <svg class="w-12 h-12 mb-3 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
          </svg>
          <p class="font-medium">No recent activity found</p>
        </div>`;
      return;
    }
    
    container.innerHTML = `
      <div class="bg-gradient-to-r from-indigo-600 to-indigo-700 p-4 rounded-t-lg shadow-md">
        <h3 class="text-white font-semibold text-lg">Recent Activity</h3>
        <p class="text-indigo-100 text-sm">Track your latest interactions</p>
      </div>
      <div class="max-h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-indigo-300 scrollbar-track-slate-100">
        <div class="activity-list p-2 space-y-3">
          ${data.activities.map(activity => `
            <div class="activity-card bg-white border border-slate-200 rounded-lg shadow-sm p-4 hover:border-indigo-400 hover:shadow-md transition-all duration-200 transform hover:-translate-y-0.5"
                data-activity-id="${activity.id}" data-org-id="${orgId}">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-100">${activity.method}</span>
                <span class="text-xs text-slate-400 font-mono">#${activity.id}</span>
              </div>
              <div class="text-sm text-slate-700">
                Recent activity using <span class="font-semibold text-indigo-600">${activity.method}</span> method
              </div>
              <div class="absolute -right-2 top-1/2 transform -translate-y-1/2 opacity-0 activity-tooltip">
                <div class="tooltip-arrow"></div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    // Add custom scrollbar styles
    const style = document.createElement('style');
    style.textContent = `
      .scrollbar-thin::-webkit-scrollbar {
        width: 6px;
      }
      .scrollbar-thin::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
      }
      .scrollbar-thin::-webkit-scrollbar-thumb {
        background: #a5b4fc;
        border-radius: 10px;
      }
      .scrollbar-thin::-webkit-scrollbar-thumb:hover {
        background: #818cf8;
      }
      .activity-card {
        cursor: pointer;
        position: relative;
      }
      .activity-tooltip {
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
      }
      .tooltip-content {
        min-width: 280px;
        transform-origin: left center;
        animation: tooltipEnter 0.2s forwards cubic-bezier(0.26, 1.04, 0.54, 1.04);
      }
      @keyframes tooltipEnter {
        0% { opacity: 0; transform: scale(0.95) translateX(-10px); }
        100% { opacity: 1; transform: scale(1) translateX(0); }
      }
      .tooltip-arrow {
        position: absolute;
        width: 10px;
        height: 10px;
        background: white;
        transform: rotate(45deg);
        left: -5px;
        top: calc(50% - 5px);
        border-left: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        z-index: 1;
      }
    `;
    document.head.appendChild(style);

    // Setup tooltips and click handlers
    document.querySelectorAll('.activity-card').forEach(card => {
      let tooltipActive = false;
      let tooltip = null;
      
      card.addEventListener('click', async (e) => {
        e.stopPropagation();
        const activityId = card.dataset.activityId;
        const orgId = card.dataset.orgId;
        
        // Hide any existing tooltips
        document.querySelectorAll('.activity-tooltip').forEach(t => {
          if (t !== tooltip) {
            t.innerHTML = '';
            t.classList.remove('opacity-100');
            t.classList.add('opacity-0');
          }
        });
        
        // Toggle tooltip
        const tooltipContainer = card.querySelector('.activity-tooltip');
        
        if (tooltipActive) {
          tooltipContainer.innerHTML = '';
          tooltipContainer.classList.remove('opacity-100');
          tooltipContainer.classList.add('opacity-0');
          tooltipActive = false;
          tooltip = null;
          return;
        }
        
        tooltipActive = true;
        tooltip = tooltipContainer;
        
        tooltipContainer.innerHTML = `
          <div class="absolute left-2 top-1/2 transform -translate-y-1/2 tooltip-content bg-white border border-slate-200 rounded-lg shadow-lg p-4 z-50">
            <div class="tooltip-arrow"></div>
            <div class="flex items-center justify-between border-b border-slate-100 pb-2 mb-3">
              <span class="text-indigo-600 font-semibold">Activity Details</span>
              <span class="text-xs bg-indigo-50 px-2 py-1 rounded text-indigo-600">#${activityId}</span>
            </div>
            <div class="text-center py-8">
              <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-indigo-500 border-t-transparent"></div>
              <p class="text-sm text-slate-500 mt-2">Loading details...</p>
            </div>
          </div>
        `;
        
        tooltipContainer.classList.remove('opacity-0');
        tooltipContainer.classList.add('opacity-100');
        
        // Position tooltip
        const tooltipContent = tooltipContainer.querySelector('.tooltip-content');
        tooltipContent.style.right = '-20px';
        
        if (activityCache[activityId]) {
          tooltipContent.innerHTML = formatActivityTooltip(activityCache[activityId]);
        } else {
          try {
            const res = await fetch(`/bookmarks/recent-activity-detail/${orgId}/${activityId}/`);
            const { activity } = await res.json();
            activityCache[activityId] = activity;
            
            if (tooltipActive) {
              tooltipContent.innerHTML = formatActivityTooltip(activity);
            }
          } catch (err) {
            tooltipContent.innerHTML = `
              <div class="tooltip-arrow"></div>
              <div class="text-red-500 p-4">
                <svg class="w-8 h-8 text-red-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p class="text-center">Error loading activity details</p>
              </div>
            `;
          }
        }
      });
      
      // Close tooltips when clicking outside
      document.addEventListener('click', () => {
        document.querySelectorAll('.activity-tooltip').forEach(tooltip => {
          tooltip.innerHTML = '';
          tooltip.classList.remove('opacity-100');
          tooltip.classList.add('opacity-0');
          tooltipActive = false;
        });
      });
    });
    
  } catch (error) {
    console.error("Failed to fetch recent activity:", error);
    container.innerHTML = `
      <div class="flex items-center bg-red-50 p-4 rounded-lg border border-red-200 text-red-700">
        <svg class="w-5 h-5 mr-3 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span class="font-medium">Error loading activity data.</span>
      </div>
    `;
  }
}

function formatActivityTooltip(activity) {
  return `
    <div class="tooltip-arrow"></div>
    <div class="max-w-xs">
      <div class="flex items-center justify-between border-b border-slate-100 pb-2 mb-3">
        <span class="text-indigo-600 font-semibold">Activity Details</span>
        <span class="text-xs bg-indigo-50 px-2 py-1 rounded text-indigo-600">#${activity.id || '—'}</span>
      </div>
      
      <div class="space-y-2 max-h-72 overflow-y-auto scrollbar-thin pr-1">
        <div class="flex">
          <div class="w-1/3 text-slate-500 text-sm font-medium">User</div>
          <div class="w-2/3 text-slate-700 font-medium">${activity.user || '—'}</div>
        </div>
        
        <div class="flex">
          <div class="w-1/3 text-slate-500 text-sm font-medium">Path</div>
          <div class="w-2/3 text-slate-700 text-sm break-words">${activity.path || '—'}</div>
        </div>
        
        <div class="flex">
          <div class="w-1/3 text-slate-500 text-sm font-medium">Type</div>
          <div class="w-2/3">
            <span class="text-xs font-medium px-2 py-1 rounded-full bg-emerald-50 text-emerald-600">
              ${activity.activity_type || '—'}
            </span>
          </div>
        </div>
        
        <div class="flex">
          <div class="w-1/3 text-slate-500 text-sm font-medium">Model</div>
          <div class="w-2/3 text-slate-700 text-sm">${activity.model_name || '—'}</div>
        </div>
        
        <div class="flex">
          <div class="w-1/3 text-slate-500 text-sm font-medium">Object ID</div>
          <div class="w-2/3 text-slate-700 font-mono text-xs">${activity.object_id || '—'}</div>
        </div>
        
        <div class="flex">
          <div class="w-1/3 text-slate-500 text-sm font-medium">IP</div>
          <div class="w-2/3 text-slate-700 font-mono text-xs">${activity.ip_address || '—'}</div>
        </div>
        
        <div class="flex">
          <div class="w-1/3 text-slate-500 text-sm font-medium">Agent</div>
          <div class="w-2/3 text-slate-700 text-xs break-words">${activity.user_agent?.slice(0, 100) || '—'}</div>
        </div>
        
        <div class="flex">
          <div class="w-1/3 text-slate-500 text-sm font-medium">Time</div>
          <div class="w-2/3">
            <span class="text-xs font-medium px-2 py-1 rounded bg-slate-100 text-slate-600">
              ${activity.timestamp || '—'}
            </span>
          </div>
        </div>
      </div>
      
      <div class="pt-3 mt-2 border-t border-slate-100 flex justify-end">
        <button class="text-xs px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 rounded-md transition-colors duration-200 font-medium">
          View Details
        </button>
      </div>
    </div>
  `;
}