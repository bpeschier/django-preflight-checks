from django import apps


class DeployChecksAppConfig(apps.AppConfig):
    name = 'preflight'

    def ready(self):
        from . import checks
