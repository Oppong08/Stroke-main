from django.apps import AppConfig


class PatientsystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patientsystem'

    def ready(self):
        import patientsystem.signals
