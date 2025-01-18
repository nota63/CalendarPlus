self.addEventListener('push', function(event) {
    var options = {
        body: event.data ? event.data.text() : 'New Notification!',
        icon: 'icon.png', // Notification icon
        badge: 'badge.png' // Notification badge
    };

    event.waitUntil(
        self.registration.showNotification('New Notification', options)
    );
});
