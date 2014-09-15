import logging
import pwd
import os

from django.core.checks import register, Error, Warning
from django.conf import settings
from django import apps

E001 = Error(
    'Raven config is not set.',
    id='preflight_reporting.E001'
)

E002 = Error(
    'Raven config is not complete.',
    id='preflight_reporting.E002'
)

E003 = Error(
    'Raven is disabled.',
    id='preflight_reporting.E003'
)

E004 = Error(
    'Raven could not send test message.',
    id='preflight_reporting.E004'
)

E005 = Error(
    'Raven is in INSTALLED_APPS, but the package is not installed.',
    id='preflight_reporting.E005'
)

W001 = Warning(
    'Raven is not installed.',
    id='preflight_reporting.W001'
)


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_reporting(app_configs, **kwargs):
    errors = []

    current_user = pwd.getpwuid(os.getuid()).pw_name

    # Get all configs if we don't get a specific set
    if not app_configs:
        app_configs = apps.apps.app_configs.values()

    raven_installed = bool(list(filter(lambda app: app.name == "raven.contrib.django.raven_compat", app_configs)))
    if not raven_installed:
        errors.append(W001)
    else:
        raven_config = getattr(settings, 'RAVEN_CONFIG', None)
        if raven_config is None or not isinstance(raven_config, dict):
            errors.append(E001)

        try:
            # noinspection PyPackageRequirements,PyUnresolvedReferences
            from raven.contrib.django.models import client

            # So we are duplicating code from manage.py raven test here...

            if not all([client.servers, client.project, client.public_key, client.secret_key]):
                errors.append(E002)

            if not client.is_enabled():
                errors.append(E003)
            else:
                # Test sending
                data = {
                    'culprit': 'preflight.checks.check_reporting',
                    'logger': 'raven.test',
                    'request': {
                        'method': 'GET',
                        'url': 'http://example.com',
                    }
                }
                ident = client.get_ident(client.captureMessage(
                    message='This is a test message generated using ``raven test``',
                    data=data,
                    level=logging.INFO,
                    stack=True,
                    tags={},
                    extra={
                        'user': current_user,
                        'loadavg': os.getloadavg(),
                    },
                ))

                if client.state.did_fail():
                    errors.append(E004)

        except ImportError:
            errors.append(E005)

    # TODO: check if we actually log something

    return errors
