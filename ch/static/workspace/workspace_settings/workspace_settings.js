// Handle workspace creation
document.getElementById('createOrgBtn').addEventListener('click', function () {
    const existingModal = document.getElementById('createOrgModal');
    if (existingModal) existingModal.remove(); // prevent duplicates

    const modalHTML = `
    <div class="modal fade" id="createOrgModal" tabindex="-1" aria-labelledby="createOrgModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content shadow-lg rounded-4">
          <div class="modal-header">
            <h5 class="modal-title" id="createOrgModalLabel">Create Organization & Invite Members</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form id="orgInviteForm">
              <div class="mb-3">
                <label class="form-label">Organization Name</label>
                <input type="text" class="form-control" name="name" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea class="form-control" name="description"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Status</label>
                <select class="form-select" name="status">
                  <option value="working_remotely">Working Remotely</option>
                  <option value="in_office">In Office</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>
              <hr>
              <div id="invitesWrapper">
                <h6>Invite Members</h6>
                <div class="invite-field mb-3 d-flex gap-2">
                  <input type="email" class="form-control" placeholder="Email" required>
                  <select class="form-select" required>
                    <option value="manager">Manager</option>
                    <option value="employee">Employee</option>
                  </select>
                  <button type="button" class="btn btn-danger remove-invite">×</button>
                </div>
              </div>
              <button type="button" class="btn btn-outline-primary mb-3" id="addInviteBtn">+ Add Another</button>
            </form>
          </div>
          <div class="modal-footer">
            <button type="submit" form="orgInviteForm" class="btn btn-success">Create & Invite</button>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          </div>
        </div>
      </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Add dynamic invite field logic
    document.getElementById('addInviteBtn').addEventListener('click', () => {
      const field = `
        <div class="invite-field mb-3 d-flex gap-2">
          <input type="email" class="form-control" placeholder="Email" required>
          <select class="form-select" required>
            <option value="manager">Manager</option>
            <option value="employee">Employee</option>
          </select>
          <button type="button" class="btn btn-danger remove-invite">×</button>
        </div>`;
      document.getElementById('invitesWrapper').insertAdjacentHTML('beforeend', field);
    });

    // Remove invite field
    document.addEventListener('click', function (e) {
      if (e.target.classList.contains('remove-invite')) {
        e.target.closest('.invite-field').remove();
      }
    });

    // Form submit AJAX
    document.getElementById('orgInviteForm').addEventListener('submit', function (e) {
      e.preventDefault();

      const form = e.target;
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
        if (data.success) {
          alert(data.message);
          bootstrap.Modal.getInstance(document.getElementById('createOrgModal')).hide();
          form.reset();
        } else {
          alert("Error: " + (data.error || "Something went wrong!"));
        }
      })
      .catch(err => {
        console.error(err);
        alert("AJAX error occurred.");
      });
    });

    // Show modal
    new bootstrap.Modal(document.getElementById('createOrgModal')).show();
});