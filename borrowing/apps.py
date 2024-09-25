from django.apps import AppConfig


class BorowingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowing"

    def ready(self):
        import borrowing.signals
