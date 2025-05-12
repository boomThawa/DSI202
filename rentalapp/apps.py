# rentalapp/apps.py

from django.apps import AppConfig

class RentalappConfig(AppConfig):
    name = 'rentalapp'

    def ready(self):
        import rentalapp.signals  # เพิ่มการโหลด signals
