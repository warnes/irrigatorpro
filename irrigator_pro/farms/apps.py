from django.apps import AppConfig

class FarmsConfig(AppConfig):
    name = 'farms'
    verbose_name = "Farms"

    def ready(self):

        import farms.signals
