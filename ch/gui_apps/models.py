from django.db import models
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from accounts.models import Organization, Profile
from django.core.exceptions import ValidationError



User = get_user_model()
# Create your models here.
class AutoSchedule(models.Model):
    class RecurrenceChoices(models.TextChoices):
        DAILY = "daily", _("Every Day")
        WEEKLY = "weekly", _("Every Week")
        BIWEEKLY = "biweekly", _("Every 2 Weeks")
        MONTHLY = "monthly", _("Every Month")
        MONDAY = "monday", _("Every Monday")
        TUESDAY = "tuesday", _("Every Tuesday")
        WEDNESDAY = "wednesday", _("Every Wednesday")
        THURSDAY = "thursday", _("Every Thursday")
        FRIDAY = "friday", _("Every Friday")
        CUSTOM = "custom", _("Custom Date")  # 🆕 Added Custom Option

    class StatusChoices(models.TextChoices):
        PENDING = "pending", _("Pending")
        SCHEDULED = "scheduled", _("Scheduled")
        SKIPPED = "skipped", _("Skipped")
        FAILED = "failed", _("Failed")

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="auto_schedules",
        db_index=True,
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_auto_schedules",
        db_index=True,
    )
    scheduled_with = models.ManyToManyField(
        User,
        related_name="auto_schedules",
    )
    meeting_title=models.CharField(max_length=100)
    time = models.TimeField(help_text="Time of the meeting")
    recurrence = models.CharField(
        max_length=20,
        choices=RecurrenceChoices.choices,
        default=RecurrenceChoices.WEEKLY,
        help_text="Defines how often this meeting should be scheduled",
    )
    custom_date = models.DateField(
        null=True,
        blank=True,
        help_text="Only required if 'Custom Date' is selected.",
    )  # 🆕 Custom Date Field

    skip_if_busy = models.BooleanField(
        default=False,
        help_text="If checked, meeting will be skipped if participants are busy.",
    )

    remind_check= models.BooleanField(
        default=False,
        help_text="If checked, we will remind both creator and scheduler before meeting.",
    )

    retry_if_failed= models.BooleanField(
        default=False,
        help_text="If checked,CalendarPlus will retry the meeting to schedule if failed!.",
    )


    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
    )

    conflict_detected = models.BooleanField(
        default=False,
        help_text="System will set this to True if scheduling conflicts are found.",
    )
    last_attempted_schedule = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last scheduling attempt.",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization"]),
            models.Index(fields=["creator"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"AutoMeeting {self.pk} ({self.recurrence}) - {self.status}"

    def clean(self):
        """Ensure custom_date is provided only when recurrence is 'custom'."""
        if self.recurrence == self.RecurrenceChoices.CUSTOM and not self.custom_date:
            raise ValidationError(_("Custom date is required when recurrence is 'Custom Date'."))

        if self.recurrence != self.RecurrenceChoices.CUSTOM and self.custom_date:
            raise ValidationError(_("Custom date should be empty unless 'Custom Date' is selected."))

    def check_availability(self):
        """Industry-level availability check logic (to be implemented)."""
        pass
