function EventCalendar(orgId) {
    const calendarEl = document.getElementById('eventCalendar');
  
    // Clear previous calendar instance
    if (calendarEl.innerHTML.trim() !== '') {
      calendarEl.innerHTML = '';
    }
  
    // Add Tailwind classes to calendar container
    calendarEl.className = 'rounded-lg shadow-lg bg-white overflow-hidden border border-gray-100';
  
    fetch(`/event_widget/user-events-calendar/${orgId}/`)
      .then(response => response.json())
      .then(events => {
        const calendar = new FullCalendar.Calendar(calendarEl, {
          initialView: 'dayGridMonth',
          themeSystem: 'bootstrap5',
          height: 'auto',
          contentHeight: 'auto',
          aspectRatio: 1.35, // More compact ratio
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
            showEventModal('Loading...', '<div class="flex justify-center items-center p-4"><div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-indigo-500"></div></div>');
  
            fetch(detailUrl)
              .then(res => res.json())
              .then(data => {
                const event = data.event;
                const bookings = data.bookings;
  
                let bookingsHTML = '<div class="mt-4">';
                if (bookings.length === 0) {
                  bookingsHTML += `<div class="text-gray-500 text-sm italic py-2">No bookings yet.</div>`;
                } else {
                  bookingsHTML += `<div class="space-y-2">`;
                  bookings.forEach(b => {
                    bookingsHTML += `
                      <div class="flex justify-between items-start bg-gray-50 rounded-lg p-3 hover:bg-gray-100">
                        <div>
                          <div class="font-medium text-gray-800">${b.invitee}</div>
                          <div class="text-xs text-gray-500">${b.start_time} - ${b.end_time}</div>
                        </div>
                        <span class="px-2 py-1 text-xs font-medium rounded-full ${getBadgeColor(b.status)}">${b.status}</span>
                      </div>`;
                  });
                  bookingsHTML += '</div>';
                }
                bookingsHTML += '</div>';
  
                const html = `
                  <div class="space-y-4">
                    <div class="space-y-2">
                      <div class="flex items-center space-x-2">
                        <div class="w-2 h-2 rounded-full ${getEventTypeColor(event.event_type)}"></div>
                        <span class="text-xs uppercase tracking-wider text-gray-500 font-medium">${event.event_type.replace('_', ' ')}</span>
                      </div>
                      
                      <div class="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <div class="text-gray-500 font-medium">Location</div>
                          <div class="text-gray-800">${event.location || 'Not specified'}</div>
                        </div>
                        <div>
                          <div class="text-gray-500 font-medium">Duration</div>
                          <div class="text-gray-800">${event.duration || 'N/A'} mins</div>
                        </div>
                        <div>
                          <div class="text-gray-500 font-medium">Recurring</div>
                          <div class="text-gray-800">${event.is_recurring ? 'Yes' : 'No'}</div>
                        </div>
                      </div>
                    </div>
                    
                    <div class="pt-2">
                      <div class="text-gray-500 font-medium mb-1">Description</div>
                      <div class="text-gray-700 text-sm bg-gray-50 p-3 rounded-lg">${event.description || 'No description available'}</div>
                    </div>
                    
                    <div class="pt-2">
                      <div class="flex items-center justify-between mb-2">
                        <div class="text-gray-500 font-medium">Bookings</div>
                        <div class="text-xs text-indigo-600 font-medium">${bookings.length} total</div>
                      </div>
                      ${bookingsHTML}
                    </div>
                  </div>
                `;
  
                showEventModal(event.title, html);
              })
              .catch(err => {
                console.error('Error loading event:', err);
                showEventModal('Error', '<div class="text-red-500 text-center py-4">Could not fetch event data. Please try again later.</div>');
              });
          },
          eventDidMount: function(info) {
            // Apply custom styling to event element without class conflicts
            info.el.style.borderRadius = '4px';
            info.el.style.boxShadow = '0 1px 2px rgba(0,0,0,0.05)';
            
            // Use data attribute to store event type
            if (info.event.extendedProps.event_type) {
              const eventType = info.event.extendedProps.event_type.toLowerCase();
              info.el.setAttribute('data-event-type', eventType);
              
              // Add left border based on event type
              info.el.style.borderLeft = '3px solid ' + getEventTypeColorHex(eventType);
            }
            
            new bootstrap.Tooltip(info.el, {
              title: info.event.extendedProps.description || 'No description',
              placement: 'top',
              trigger: 'hover',
              container: 'body',
              template: `
                <div class="tooltip" role="tooltip">
                  <div class="tooltip-inner bg-gray-800 text-white px-3 py-2 rounded text-xs max-w-xs"></div>
                </div>
              `
            });
          }
        });
  
        calendar.render();
        
        // Apply styles after calendar is rendered
        setTimeout(() => {
          // Style the calendar header
          const headers = calendarEl.querySelectorAll('.fc-toolbar');
          headers.forEach(header => {
            header.style.padding = '0.75rem 1rem';
            header.style.backgroundColor = '#f9fafb';
            header.style.borderBottom = '1px solid #f3f4f6';
          });
          
          // Style the title
          const titles = calendarEl.querySelectorAll('.fc-toolbar-title');
          titles.forEach(title => {
            title.style.fontSize = '1rem';
            title.style.fontWeight = '500';
            title.style.color = '#111827';
          });
          
          // Style buttons
          const buttons = calendarEl.querySelectorAll('.fc-button');
          buttons.forEach(button => {
            button.style.fontSize = '0.875rem';
            button.style.padding = '0.375rem 0.75rem';
            button.style.borderRadius = '0.375rem';
            button.style.backgroundColor = '#ffffff';
            button.style.color = '#374151';
            button.style.border = '1px solid #e5e7eb';
            button.style.boxShadow = '0 1px 2px rgba(0,0,0,0.05)';
            
            // Add hover effect
            button.addEventListener('mouseenter', () => {
              button.style.backgroundColor = '#f9fafb';
            });
            button.addEventListener('mouseleave', () => {
              if (!button.classList.contains('fc-button-active')) {
                button.style.backgroundColor = '#ffffff';
              }
            });
          });
          
          // Style active buttons
          const activeButtons = calendarEl.querySelectorAll('.fc-button-active');
          activeButtons.forEach(button => {
            button.style.backgroundColor = '#eff6ff';
            button.style.color = '#3b82f6';
            button.style.borderColor = '#bfdbfe';
          });
          
          // Style day cells
          const dayCells = calendarEl.querySelectorAll('.fc-daygrid-day');
          dayCells.forEach(cell => {
            cell.style.transition = 'background-color 0.15s ease';
            
            cell.addEventListener('mouseenter', () => {
              cell.style.backgroundColor = '#f3f4f6';
            });
            cell.addEventListener('mouseleave', () => {
              cell.style.backgroundColor = '';
            });
          });
          
          // Style event cells
          const eventCells = calendarEl.querySelectorAll('.fc-event');
          eventCells.forEach(eventCell => {
            eventCell.style.padding = '0.125rem 0.25rem';
            eventCell.style.fontSize = '0.75rem';
            eventCell.style.cursor = 'pointer';
          });
          
          // Make table more compact
          const dayNumbers = calendarEl.querySelectorAll('.fc-daygrid-day-number');
          dayNumbers.forEach(num => {
            num.style.fontSize = '0.75rem';
            num.style.padding = '0.25rem';
          });
          
        }, 100);
      })
      .catch(error => {
        console.error('Failed to load events:', error);
        calendarEl.innerHTML = `<div class="flex items-center justify-center p-8 text-red-500">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
          </svg>
          Failed to load calendar. Try again later
        </div>`;
      });
  }
  
  // Helper to show modal
  function showEventModal(title, bodyHTML) {
    let modal = document.getElementById('eventDetailsModal');
    if (!modal) {
      document.body.insertAdjacentHTML('beforeend', `
        <div id="eventDetailsModal" class="fixed inset-0 z-50 flex items-center justify-center hidden" style="background-color: rgba(0,0,0,0.5);">
          <div id="eventModalContent" class="bg-white rounded-lg shadow-xl w-full max-w-lg max-h-[90vh] overflow-hidden flex flex-col m-4" style="transform: scale(0.95); opacity: 0; transition: transform 0.2s ease, opacity 0.2s ease;">
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50">
              <h3 id="eventModalLabel" class="font-medium text-lg text-gray-800">${title}</h3>
              <button type="button" id="closeEventModal" class="text-gray-400 hover:text-gray-600">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
              </button>
            </div>
            <div id="eventModalBody" class="p-6 overflow-y-auto flex-grow">${bodyHTML}</div>
            <div class="px-6 py-4 border-t border-gray-100 flex justify-end">
              <button type="button" id="closeEventModalBtn" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-sm font-medium">Close</button>
            </div>
          </div>
        </div>
      `);
      
      modal = document.getElementById('eventDetailsModal');
      const modalContent = document.getElementById('eventModalContent');
      
      // Animation and event handlers
      setTimeout(() => {
        modal.classList.remove('hidden');
        setTimeout(() => {
          modalContent.style.transform = 'scale(1)';
          modalContent.style.opacity = '1';
        }, 10);
      }, 10);
      
      // Close handlers
      document.getElementById('closeEventModal').addEventListener('click', closeModal);
      document.getElementById('closeEventModalBtn').addEventListener('click', closeModal);
      modal.addEventListener('click', function(e) {
        if (e.target === modal) closeModal();
      });
      
      // Close modal function
      function closeModal() {
        modalContent.style.transform = 'scale(0.95)';
        modalContent.style.opacity = '0';
        setTimeout(() => {
          modal.classList.add('hidden');
        }, 200);
      }
      
    } else {
      const modalLabel = document.getElementById('eventModalLabel');
      const modalBody = document.getElementById('eventModalBody');
      if (modalLabel) modalLabel.innerText = title;
      if (modalBody) modalBody.innerHTML = bodyHTML;
      
      // Show modal with animation
      const modalContent = document.getElementById('eventModalContent');
      modal.classList.remove('hidden');
      setTimeout(() => {
        modalContent.style.transform = 'scale(1)';
        modalContent.style.opacity = '1';
      }, 10);
    }
  }
  
  // Helper for badge color
  function getBadgeColor(status) {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }
  
  // Helper for event type color (CSS classes)
  function getEventTypeColor(eventType) {
    switch (eventType.toLowerCase()) {
      case 'meeting':
      case 'meetings': return 'bg-blue-500';
      case 'call':
      case 'calls': return 'bg-purple-500';
      case 'appointment':
      case 'appointments': return 'bg-green-500';
      case 'reminder':
      case 'reminders': return 'bg-yellow-500';
      case 'deadline':
      case 'deadlines': return 'bg-red-500';
      default: return 'bg-indigo-500';
    }
  }
  
  // Helper for event type color (hex colors for inline styles)
  function getEventTypeColorHex(eventType) {
    switch (eventType) {
      case 'meeting':
      case 'meetings': return '#3b82f6'; // blue-500
      case 'call':
      case 'calls': return '#8b5cf6'; // purple-500
      case 'appointment':
      case 'appointments': return '#10b981'; // green-500
      case 'reminder':
      case 'reminders': return '#f59e0b'; // yellow-500
      case 'deadline':
      case 'deadlines': return '#ef4444'; // red-500
      default: return '#6366f1'; // indigo-500
    }
  }

  
// # Widget 2) Team availability Heatmap------------------------------------------------------------------------------------------------------------

function TeamAvailabilityHeatmap(orgId) {
  const container = document.getElementById("availability-heatmap-widget");
  container.innerHTML = `<div class="text-center text-gray-500">Loading team availability...</div>`;

  fetch(`/event_widget/team-availability-heatmap/${orgId}/`)
    .then(res => res.json())
    .then(data => {
      const days = data.days_of_week;
      const users = data.heatmap;

      let html = `
        <div class="overflow-x-auto border rounded-xl shadow-sm bg-white">
          <table class="min-w-full text-sm text-left text-gray-700">
            <thead class="bg-gray-100 text-xs uppercase font-semibold text-gray-600 sticky top-0 z-10">
              <tr>
                <th class="p-3 border-r">User</th>
                ${days.map(day => `<th class="p-3 text-center">${day}</th>`).join('')}
              </tr>
            </thead>
            <tbody>
      `;

      users.forEach(user => {
        html += `<tr class="border-t hover:bg-indigo-50 transition">
                  <td class="p-3 flex items-center gap-2 border-r">
                    <img src="${user.profile_picture || '/static/default-avatar.png'}"
                         alt="${user.full_name}" class="w-8 h-8 rounded-full border object-cover">
                    <span class="text-sm font-medium">${user.full_name}</span>
                  </td>`;

        for (let i = 0; i < 7; i++) {
          const slots = user.availability[i] || [];
          let cellColor = "bg-gray-100";
          if (slots.length > 0) {
            const allBooked = slots.every(s => s.is_booked);
            const allAvailable = slots.every(s => !s.is_booked);
            const partial = !allBooked && !allAvailable;

            cellColor = allAvailable ? "bg-green-200" : allBooked ? "bg-red-300" : "bg-yellow-200";
          }

          html += `<td class="p-3 text-center ${cellColor} cursor-pointer relative group" data-user="${user.user_id}" data-day="${i}">
                      <div class="text-xs">${slots.length > 0 ? slots.length + " slot(s)" : "-"}</div>

                      <!-- Tooltip on hover -->
                      ${slots.length > 0 ? `
                        <div class="absolute left-1/2 -translate-x-1/2 mt-1 z-50 hidden group-hover:block w-max bg-white border border-gray-300 p-2 rounded-lg shadow-md text-xs text-left">
                          ${slots.map(slot => `
                            <div class="mb-1">
                              <span class="font-medium">${slot.start_time} - ${slot.end_time}</span><br>
                              ${slot.is_booked ? '<span class="text-red-500">Booked</span>' : '<span class="text-green-600">Available</span>'}
                            </div>
                          `).join('')}
                        </div>` : ''}
                    </td>`;
        }

        html += `</tr>`;
      });

      html += `</tbody></table></div>`;
      container.innerHTML = html;
    })
    .catch(err => {
      console.error("Error loading heatmap:", err);
      container.innerHTML = `<div class="text-red-500 text-center">Error loading team availability.</div>`;
    });
}



