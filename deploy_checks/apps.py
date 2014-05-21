from django import apps


class DeployChecksAppConfig(apps.AppConfig):
    name = 'deploy_checks'

    def ready(self):
        from . import checks
