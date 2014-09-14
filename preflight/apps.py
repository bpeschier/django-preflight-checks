from django import apps


class PreflightChecksAppConfig(apps.AppConfig):
    name = 'preflight'

    def ready(self):
        # noinspection PyUnresolvedReferences
        # Import it, so it gets triggered
        from . import checks
