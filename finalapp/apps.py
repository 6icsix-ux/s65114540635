from django.apps import AppConfig

class FinalappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finalapp'

    def ready(self):
        import finalapp.signals
