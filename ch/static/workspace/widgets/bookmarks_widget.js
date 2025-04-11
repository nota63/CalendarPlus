  // CSRF helper
  function getCSRFToken() {
    return document.cookie.split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
  }

  // Fetch and display the bookmarks
  async function fetchAndRenderBookmarks(orgId) {
    const widgetContainer = document.getElementById('bookmarks-content');
    widgetContainer.innerHTML = `<div class="text-gray-500 text-sm">Loading bookmarks...</div>`;

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
        widgetContainer.innerHTML = `<div class="text-gray-400 text-sm">No bookmarks found yet 💭</div>`;
        return;
      }

      // Render bookmarks
      const bookmarksHTML = data.data.map((item, index) => {
        return `
          <div class="p-3 mb-2 border rounded-lg shadow-sm hover:shadow-md transition group relative" id="bookmark-${index}">
            <div class="flex justify-between items-center">
              <a href="${item.url}" target="_blank" class="text-blue-600 font-medium hover:underline">
                ${item.title}
              </a>
              ${item.pinned ? '<span class="text-yellow-500 text-xs">📌 Pinned</span>' : ''}
            </div>
            <p class="text-sm text-gray-600 mt-1">${item.description || ''}</p>

            <!-- Delete icon -->
            <button 
              class="position-absolute top-0 end-0 m-1 btn btn-sm btn-outline-danger d-none delete-btn"
              data-id="${index}"
              title="Delete"
            >
              <i class="bi bi-trash"></i>
            </button>
          </div>
        `;
      }).join('');

      widgetContainer.innerHTML = bookmarksHTML;

      // Add hover behavior to show delete button
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
      widgetContainer.innerHTML = `<div class="text-red-500 text-sm">Failed to load bookmarks. Try again later.</div>`;
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