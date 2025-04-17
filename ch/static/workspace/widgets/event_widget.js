function EventCalendar(orgId) {
    const calendarEl = document.getElementById('eventCalendar');
  
    // Clear previous calendar instance
    if (calendarEl.innerHTML.trim() !== '') {
      calendarEl.innerHTML = '';
    }
  
    fetch(`/event_widget/user-events-calendar/${orgId}/`)
      .then(response => response.json())
      .then(events => {
        const calendar = new FullCalendar.Calendar(calendarEl, {
          initialView: 'dayGridMonth',
          themeSystem: 'bootstrap5',
          height: 'auto',
          headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listWeek'
          },
          events: events,
          eventClick: function(info) {
            info.jsEvent.preventDefault();
  
          
            const eventSlug = info.event.extendedProps.slug;
  
            if (!eventSlug || !orgId) {
              showEventModal('Error', 'Missing event details.');
              return;
            }
  
            const detailUrl = `/event_widget/event-detail-widget/${window.djangoData.orgId}/${eventSlug}/`;
  
            // Show loader in modal
            showEventModal('Loading...', 'Please wait while we fetch event details...');
  
            fetch(detailUrl)
              .then(res => res.json())
              .then(data => {
                const event = data.event;
                const bookings = data.bookings;
  
                let bookingsHTML = '<ul class="list-group">';
                if (bookings.length === 0) {
                  bookingsHTML += `<li class="list-group-item text-muted">No bookings yet.</li>`;
                } else {
                  bookings.forEach(b => {
                    bookingsHTML += `
                      <li class="list-group-item d-flex justify-content-between align-items-start">
                        <div>
                          <strong>${b.invitee}</strong><br>
                          <small>${b.start_time} - ${b.end_time}</small>
                        </div>
                        <span class="badge bg-${getBadgeColor(b.status)}">${b.status}</span>
                      </li>`;
                  });
                }
                bookingsHTML += '</ul>';
  
                const html = `
                  <h5>${event.title}</h5>
                  <p><strong>Type:</strong> ${event.event_type.replace('_', ' ')}</p>
                  <p><strong>Location:</strong> ${event.location}</p>
                  <p><strong>Duration:</strong> ${event.duration || 'N/A'} mins</p>
                  <p><strong>Recurring:</strong> ${event.is_recurring ? 'Yes' : 'No'}</p>
                  <p><strong>Description:</strong><br>${event.description || 'No description available'}</p>
                  <hr>
                  <h6>Bookings:</h6>
                  ${bookingsHTML}
                `;
  
                showEventModal(event.title, html);
              })
              .catch(err => {
                console.error('Error loading event:', err);
                showEventModal('Error', 'Could not fetch event data. Please try again later.');
              });
          },
          eventDidMount: function(info) {
            new bootstrap.Tooltip(info.el, {
              title: info.event.extendedProps.description || 'No description',
              placement: 'top',
              trigger: 'hover',
              container: 'body'
            });
          }
        });
  
        calendar.render();
      })
      .catch(error => {
        console.error('Failed to load events:', error);
        calendarEl.innerHTML = `<div class="text-danger p-2">Failed to load calendar. Try again later 💔</div>`;
      });
  }
  
  // Helper to show modal
  function showEventModal(title, bodyHTML) {
    let modal = document.getElementById('eventDetailsModal');
    if (!modal) {
      document.body.insertAdjacentHTML('beforeend', `
        <div class="modal fade" id="eventDetailsModal" tabindex="-1" aria-labelledby="eventModalLabel" aria-hidden="true">
          <div class="modal-dialog modal-lg modal-dialog-scrollable">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="eventModalLabel">${title}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">${bodyHTML}</div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              </div>
            </div>
          </div>
        </div>
      `);
      modal = document.getElementById('eventDetailsModal');
    } else {
      modal.querySelector('.modal-title').innerText = title;
      modal.querySelector('.modal-body').innerHTML = bodyHTML;
    }
  
    new bootstrap.Modal(modal).show();
  }
  
  // Helper for badge color
  function getBadgeColor(status) {
    switch (status) {
      case 'confirmed': return 'success';
      case 'pending': return 'warning';
      case 'cancelled': return 'danger';
      default: return 'secondary';
    }
  }
  