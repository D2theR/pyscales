from django.apps import AppConfig


class ExampleConfig(AppConfig):
    name = 'pyscales'

    def ready(self):
        import pyscales.signals
