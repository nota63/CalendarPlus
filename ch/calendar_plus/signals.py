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
import logging
from datetime import datetime, timedelta
from datetime import time
from django.db import IntegrityError


# Get an instance of a logger
logger = logging.getLogger(__name__)

# Define default availability slots
DEFAULT_AVAILABILITY = [
    {"day_of_week": 0, "start_time": time(9, 0), "end_time": time(17, 0)},  # Monday
    {"day_of_week": 1, "start_time": time(9, 0), "end_time": time(17, 0)},  # Tuesday
    {"day_of_week": 2, "start_time": time(9, 0), "end_time": time(17, 0)},  # Wednesday
    {"day_of_week": 3, "start_time": time(9, 0), "end_time": time(17, 0)},  # Thursday
    {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(17, 0)},  # Friday
    {"day_of_week": 5, "start_time": time(9, 0), "end_time": time(12, 0)},  # saturday
]

@receiver(post_save, sender=Profile)
def create_default_availability(sender, instance, created, **kwargs):
    """
    Signal to create default availability for a user when a Profile instance is created.
    """
    if created and instance.organization:
        try:
            existing_availability = Availability.objects.filter(
                user=instance.user,
                organization=instance.organization
            )
            if existing_availability.exists():
                logger.warning(
                    f"Default availability already exists for user {instance.user} in organization {instance.organization}. Skipping creation."
                )
                return

            for slot in DEFAULT_AVAILABILITY:
                try:
                    Availability.objects.create(
                        user=instance.user,
                        organization=instance.organization,
                        day_of_week=slot["day_of_week"],
                        start_time=slot["start_time"],
                        end_time=slot["end_time"],
                    )
                except IntegrityError as e:
                    logger.error(
                        f"Failed to create availability for user {instance.user} in organization {instance.organization}: {e}"
                    )

            logger.info(
                f"Default availability successfully created for user {instance.user} in organization {instance.organization}."
            )
        except Exception as e:
            logger.exception(
                f"An unexpected error occurred while creating availability for user {instance.user} in organization {instance.organization}: {e}"
            )




