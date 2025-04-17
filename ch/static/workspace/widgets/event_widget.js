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
  container.innerHTML = `
    <div class="flex items-center justify-center p-4 text-gray-500">
      <svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      Loading team availability...
    </div>
  `;
  
  fetch(`/event_widget/team-availability-heatmap/${orgId}/`)
    .then(res => res.json())
    .then(data => {
      const days = data.days_of_week;
      const users = data.heatmap;
      
      let html = `
      <div class="overflow-hidden rounded-lg shadow-md border border-gray-200 bg-white">
        <!-- Header -->
        <div class="p-4 border-b border-gray-200 flex justify-between items-center bg-white">
          <h3 class="text-base font-semibold text-gray-800">Team Availability</h3>
          <div class="flex space-x-4 text-xs font-medium">
            <span class="flex items-center"><span class="w-3 h-3 rounded-full bg-emerald-500 mr-2"></span> Available</span>
            <span class="flex items-center"><span class="w-3 h-3 rounded-full bg-amber-400 mr-2"></span> Partial</span>
            <span class="flex items-center"><span class="w-3 h-3 rounded-full bg-rose-500 mr-2"></span> Booked</span>
          </div>
        </div>
        
        <!-- Table Container with custom styled scrollbars -->
        <div class="overflow-auto max-h-96 custom-scrollbar">
          <table class="min-w-full border-collapse text-sm">
            <thead>
              <tr class="bg-gray-50 text-xs font-medium text-gray-500 sticky top-0 z-10 shadow-sm">
                <th class="py-3 px-4 border-r border-gray-200 text-left sticky left-0 bg-gray-50 z-20">User</th>
                ${days.map(day => `<th class="py-3 px-4 text-center">${day}</th>`).join('')}
              </tr>
            </thead>
            <tbody>
    `;
    
    users.forEach((user, index) => {
      html += `
        <tr class="border-t border-gray-200 hover:bg-blue-50/40 transition-colors duration-150">
          <td class="py-3 px-4 flex items-center gap-3 border-r border-gray-200 sticky left-0 bg-white z-10">
            <div class="w-8 h-8 rounded-full bg-gray-100 flex-shrink-0 overflow-hidden">
              <img src="${user.profile_picture || '/static/default-avatar.png'}"
                   alt="${user.full_name}"
                   class="w-full h-full object-cover">
            </div>
            <span class="font-medium text-gray-800">${user.full_name}</span>
          </td>
      `;
      
      for (let i = 0; i < 7; i++) {
        const slots = user.availability[i] || [];
        let cellColor = "bg-gray-50";
        let dotColor = "";
        let textColor = "text-gray-400";
        
        if (slots.length > 0) {
          const allBooked = slots.every(s => s.is_booked);
          const allAvailable = slots.every(s => !s.is_booked);
          
          if (allAvailable) {
            cellColor = "bg-emerald-50";
            dotColor = "bg-emerald-500";
            textColor = "text-emerald-700";
          } else if (allBooked) {
            cellColor = "bg-rose-50";
            dotColor = "bg-rose-500";
            textColor = "text-rose-700";
          } else {
            cellColor = "bg-amber-50";
            dotColor = "bg-amber-400";
            textColor = "text-amber-700";
          }
        }
        
        html += `
          <td class="py-3 px-4 text-center ${cellColor} cursor-pointer relative group transition-colors duration-150" data-user="${user.user_id}" data-day="${i}">
            <div class="flex flex-col items-center justify-center">
              ${slots.length > 0 ? 
                `<div class="flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full ${dotColor}"></span>
                  <span class="text-xs font-medium ${textColor}">${slots.length} slot${slots.length > 1 ? 's' : ''}</span>
                 </div>` : 
                `<span class="text-xs text-gray-400">-</span>`
              }
            </div>
            
            <!-- Enhanced tooltip -->
            ${slots.length > 0 ? `
              <div class="absolute left-1/2 -translate-x-1/2 top-full mt-2 z-50 hidden group-hover:block w-64 bg-white border border-gray-200 p-3 rounded-md shadow-lg text-xs text-left">
                <div class="font-medium text-gray-700 mb-2 pb-2 border-b border-gray-100">Availability Details</div>
                ${slots.map(slot => `
                  <div class="mb-2 ${slot !== slots[slots.length-1] ? 'border-b border-gray-100 pb-2' : ''}">
                    <div class="flex justify-between items-center mb-1">
                      <span class="font-medium text-gray-800">${slot.start_time} - ${slot.end_time}</span>
                      ${slot.is_booked ?
                        '<span class="px-2 py-1 rounded-full bg-rose-100 text-rose-700 text-xs font-medium">Booked</span>' :
                        '<span class="px-2 py-1 rounded-full bg-emerald-100 text-emerald-700 text-xs font-medium">Available</span>'
                      }
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : ''}
          </td>
        `;
      }
      
      html += `</tr>`;
    });
    
    html += `
            </tbody>
          </table>
        </div>
      </div>
    
      <style>
        /* Modern custom scrollbar styles */
        .custom-scrollbar {
          scrollbar-width: thin; /* For Firefox */
          scrollbar-color: rgba(203, 213, 225, 0.5) transparent; /* For Firefox */
        }
        
        /* Chrome, Edge, and Safari */
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
          border-radius: 10px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: rgba(203, 213, 225, 0.5);
          border-radius: 10px;
          transition: background-color 0.2s ease;
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background-color: rgba(148, 163, 184, 0.7);
        }
        
        /* For IE and Edge legacy support */
        .custom-scrollbar {
          -ms-overflow-style: auto;
        }
        
        /* Make sure the User column sticks to the left when scrolling horizontally */
        .sticky-left {
          position: sticky;
          left: 0;
          z-index: 10;
        }
      </style>
    `;
    
    container.innerHTML = html;
    })


    .catch(err => {
      console.error("Error loading heatmap:", err);
      container.innerHTML = `
        <div class="text-red-500 text-center p-3 bg-white rounded-lg border border-red-100 shadow-sm">
          <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          Error loading team availability.
        </div>
      `;
    });
}