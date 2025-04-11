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
      const bookmarksHTML = data.data.map((item) => {
        return `
          <div class="p-3 mb-2 border rounded-lg shadow-sm hover:shadow-md transition">
            <div class="flex justify-between items-center">
              <a href="${item.url}" target="_blank" class="text-blue-600 font-medium hover:underline">
                ${item.title}
              </a>
              ${item.pinned ? '<span class="text-yellow-500 text-xs">📌 Pinned</span>' : ''}
            </div>
            <p class="text-sm text-gray-600 mt-1">${item.description || ''}</p>
          </div>
        `;
      }).join('');

      widgetContainer.innerHTML = bookmarksHTML;

    } catch (error) {
      console.error("Failed to fetch bookmarks:", error);
      widgetContainer.innerHTML = `<div class="text-red-500 text-sm">Failed to load bookmarks. Try again later.</div>`;
    }
  }

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