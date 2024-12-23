from django.contrib.auth.models import User
from .models import HolidayOrganization, Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Predefined list of government holidays (adjust according to your country)
GOVERNMENT_HOLIDAYS = [
    {"name": "New Year's Day", "start_date": "2024-01-01", "end_date": "2024-01-01"},
    {"name": "Martin Luther King Jr. Day", "start_date": "2024-01-15", "end_date": "2024-01-15"},
    {"name": "Presidents' Day", "start_date": "2024-02-19", "end_date": "2024-02-19"},
    {"name": "Memorial Day", "start_date": "2024-05-27", "end_date": "2024-05-27"},
    {"name": "Independence Day", "start_date": "2024-07-04", "end_date": "2024-07-04"},
    {"name": "Labor Day", "start_date": "2024-09-02", "end_date": "2024-09-02"},
    {"name": "Columbus Day", "start_date": "2024-10-14", "end_date": "2024-10-14"},
    {"name": "Veterans Day", "start_date": "2024-11-11", "end_date": "2024-11-11"},
    {"name": "Thanksgiving Day", "start_date": "2024-11-28", "end_date": "2024-11-28"},
    {"name": "Christmas Day", "start_date": "2024-12-25", "end_date": "2024-12-25"},
]

# Now update the signal to create these holidays for the organization when a profile is created.



@receiver(post_save, sender=Profile)
def create_predefined_holidays(sender, instance, created, **kwargs):
    """
    Signal to create predefined government holidays for a user based on their profile's organization.
    Triggered when a new Profile is created.
    """
    if created:
        organization = instance.organization
        user = instance.user  # Get the user who is creating the profile

        # Create predefined government holidays for the organization if they don't exist
        for holiday in GOVERNMENT_HOLIDAYS:
            # Check if the holiday already exists for this organization
            if not HolidayOrganization.objects.filter(organization=organization, start_date=holiday['start_date'], end_date=holiday['end_date']).exists():
                # Create holiday with user responsible for the holiday
                HolidayOrganization.objects.create(
                    organization=organization,
                    user=user,  # Assign the user who created the holiday
                    name=holiday['name'],
                    start_date=holiday['start_date'],
                    end_date=holiday['end_date'],
                    description=f"Government holiday for {holiday['name']}",
                )
                print(f"Predefined holiday created: {holiday['name']} for organization {organization.name} by {user.username}")








