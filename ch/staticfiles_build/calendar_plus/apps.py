from django.apps import AppConfig


class calendarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendar_plus'

    def ready(self):
        import calendar_plus.signals

