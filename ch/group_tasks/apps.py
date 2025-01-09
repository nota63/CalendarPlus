from django.apps import AppConfig


class GroupTasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'group_tasks'

    def ready(self):
        import group_tasks.signals
        
