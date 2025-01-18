from django.apps import AppConfig


class OrganizationChannelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'organization_channels'

    def ready(self):
        import organization_channels.signals
