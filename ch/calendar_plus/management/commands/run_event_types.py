from django.core.management.base import BaseCommand
from django.contrib.auth.models import User  # Replace with custom User if applicable
from calendar.models import EventType

class Command(BaseCommand):
    help = "Populates predefined Event Types"

    def handle(self, *args, **kwargs):
        admin_user = User.objects.first()  # Replace with specific user logic if needed

        event_types = [
            {"name": "One-on-One Meeting", "description": "A private meeting between two participants.", "duration": 30, "max_participants": 2, "buffer_time": 10},
            {"name": "Group Meeting", "description": "A meeting with multiple participants.", "duration": 60, "max_participants": 10, "buffer_time": 15},
            {"name": "Collective Meeting", "description": "A meeting where multiple people select timeslots.", "duration": 45, "max_participants": 5, "buffer_time": 10},
        ]

        for event in event_types:
            EventType.objects.update_or_create(
                name=event["name"],
                user=admin_user,  # Ensure ownership is set
                defaults=event
            )

        self.stdout.write(self.style.SUCCESS("Event types populated successfully."))
