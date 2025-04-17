function EventCalendar(orgId) {
    const calendarEl = document.getElementById('eventCalendar');
  
    // Clear any previous calendar instance
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
            info.jsEvent.preventDefault(); // don't navigate by default
  
            if (info.event.url) {
              window.open(info.event.url, '_blank'); // or redirect directly
            }
          },
          eventDidMount: function(info) {
            // Optional tooltip
            const tooltip = new bootstrap.Tooltip(info.el, {
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
  