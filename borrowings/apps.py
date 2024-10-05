from django.apps import AppConfig


class BorowingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowings"

    def ready(self):
        import borrowings.signals
