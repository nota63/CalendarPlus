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