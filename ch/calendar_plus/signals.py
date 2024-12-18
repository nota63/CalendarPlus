from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from accounts.models import Availability, Organization
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from accounts.models import Profile
from django.db.models import Q
from django.db import transaction
from django.utils.timezone import datetime
from datetime import timedelta
from django.db.utils import IntegrityError




DEFAULT_SCHEDULE = [
    {"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"},
    {"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "17:00"},
    {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
    {"day_of_week": "Thursday", "start_time": "09:00", "end_time": "17:00"},
    {"day_of_week": "Friday", "start_time": "09:00", "end_time": "17:00"},
    {"day_of_week": "Saturday", "start_time": "10:00", "end_time": "14:00"},
    {"day_of_week": "Sunday", "start_time": None, "end_time": None},
]

@receiver(post_save, sender=Profile)
def create_availability_for_user_in_org(sender, instance, created, **kwargs):
    """
    Signal to create availability for a user when they are assigned a role in an organization.
    """
    if created or instance.is_admin or instance.is_manager or instance.is_employee:
        try:
        
            if not Availability.objects.filter(user=instance.user, organization=instance.organization).exists():
                with transaction.atomic():
                    for schedule in DEFAULT_SCHEDULE:
                        if schedule["start_time"] and schedule["end_time"]:
                            start_time = datetime.strptime(schedule["start_time"], "%H:%M").time()
                            end_time = datetime.strptime(schedule["end_time"], "%H:%M").time()

                         
                            Availability.objects.create(
                                user=instance.user,
                                organization=instance.organization,
                                day_of_week=schedule["day_of_week"],
                                start_time=start_time,
                                end_time=end_time,
                                is_booked=False,
                            )
        except Exception as e:
            print(f"Error creating availability for user {instance.user.username} in organization {instance.organization.name}: {e}")


# monday -- 09:00 - 17:00  

# monday - 09:00 - 09:30 








