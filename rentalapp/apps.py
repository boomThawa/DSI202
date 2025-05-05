from django.apps import AppConfig

class RentalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rentalapp"

    def ready(self):
        # Ensure signals register
        import rentalapp.models
