from django.apps import AppConfig


class MishmarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mishmar'

    def ready(self):
        import mishmar.signals
