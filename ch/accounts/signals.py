from django.contrib.auth.models import User
from .models import HolidayOrganization, Profile,Organization
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from organization_channels.models import Channel
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags







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







# Create a social channel by default for every organization
@receiver(post_save, sender=Organization)
def create_social_channel_and_send_email(sender, instance, created, **kwargs):
    if created:  # Only run when a new organization is created
        try:
            # ✅ Get the admin profile
            admin_profile = Profile.objects.get(organization=instance, is_admin=True)
            admin_user = admin_profile.user  # Get the admin user

            # ✅ Create "Social" Channel
            Channel.objects.create(
                organization=instance,
                created_by=admin_user,
                name="Social",
                type="BLANK",
                visibility="PUBLIC",
            )

            # ✅ Send Email to Admin
            subject = "🎉 Your Organization Has Been Created!"
            context = {
                "admin_name": admin_user.get_full_name(),
                "admin_email": admin_user.email,
                "org_name": instance.name,
                "created_at": instance.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            html_message = render_to_string("channels/creation/org_created.html", context)
            plain_message = strip_tags(html_message)  # Convert HTML to plain text
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_user.email],
                html_message=html_message,
            )
        except Profile.DoesNotExist:
            # Handle the case where no admin profile is found
            print(f"Error: Admin profile not found for organization: {instance.name}")
        except Exception as e:
            # General error handling
            print(f"Error creating channel or sending email: {e}")


