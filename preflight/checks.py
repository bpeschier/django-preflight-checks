import pwd
import os

from django.core import mail
from django import apps
from django.core.checks import register, Error, Warning
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import logging


CURRENT_USER = pwd.getpwuid(os.getuid()).pw_name
TARGET_USER = getattr(settings, 'DEPLOY_TARGET_USER', None)


#
# Internal checks
#

# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_user(app_configs, **kwargs):
    errors = []
    if TARGET_USER is None:
        errors.append(Warning(
            'No DEPLOY_TARGET_USER set, define it to check write permissions on storages',
            id='preflight.W001'
        ))

    if TARGET_USER and TARGET_USER != CURRENT_USER:
        errors.append(Warning(
            'You are not running as DEPLOY_TARGET_USER, writeable-checks can not be trusted',
            id='preflight.W002'
        ))

    return errors


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_debug(app_configs, **kwargs):
    errors = []

    if settings.DEBUG:
        errors.append(Error(
            'DEBUG is still True',
            id='deploy_debug.E001'
        ))

    if settings.DEBUG_PROPAGATE_EXCEPTIONS:
        errors.append(Error(
            'DEBUG_PROPAGATE_EXCEPTIONS is still True',
            id='deploy_debug.E002'
        ))

    # Get all configs if we don't get a specific set
    if not app_configs:
        app_configs = apps.apps.app_configs.values()

    debug_toolbar = list(filter(lambda app: app.name == "debug_toolbar", app_configs))
    if debug_toolbar:
        errors.append(Warning(
            'Debug toolbar is installed',
            id='deploy_debug.W001'
        ))

        if hasattr(settings, 'DEBUG_TOOLBAR_PATCH_SETTINGS') and settings.DEBUG_TOOLBAR_PATCH_SETTINGS:
            errors.append(Warning(
                'Debug toolbar is activated',
                id='deploy_debug.W002'
            ))

    return errors


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_databases(app_configs, **kwargs):
    errors = []

    # Check the default database
    database = settings.DATABASES.get('default')
    if database is not None:
        if database.get('ENGINE') == 'django.db.backends.sqlite3':
            errors.append(Warning(
                'The default database is a SQLite database',
                id='deploy_database.W001'
            ))

        if database.get('CONN_MAX_AGE') is 0:
            errors.append(Warning(
                """Database connection age (CONN_MAX_AGE) is 0; """
                """you might want to set it to something more persistent""",
                id='deploy_database.W002'
            ))

    return errors


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_caches(app_configs, **kwargs):
    errors = []

    cache = settings.CACHES.get('default')
    if cache is not None:
        if cache.get('BACKEND') == 'django.core.cache.backends.locmem.LocMemCache':
            errors.append(Error(
                'The cache backend is still set to local memory, install a real cache or set it to dummy',
                id='deploy_cache.E001'
            ))

    return errors


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_file_storage(app_configs, **kwargs):
    errors = []

    # Check if storage is writeable
    try:
        path = default_storage.save('__test', ContentFile('new content'))
    except IOError:
        errors.append(Error(
            'Default storage is not writeable',
            id='deploy_file_storage.E001'
        ))
    else:
        default_storage.delete(path)

    # TODO: max size, permissions?

    return errors


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_email(app_configs, **kwargs):
    errors = []

    # Check for debug-ish email backends
    if settings.EMAIL_BACKEND in [
        'django.core.mail.backends.console.EmailBackend',
        'django.core.mail.backends.filebased.EmailBackend',
        'django.core.mail.backends.locmem.EmailBackend',
    ]:
        errors.append(Error(
            'EMAIL_BACKEND is set to a testing/debug backend',
            id='deploy_email.E001'
        ))

    # So we assume if you set the dummy backend, you are not interested in mail,
    # otherwise you would have used on of the other ones to actually see mails
    # being sent.
    if settings.EMAIL_BACKEND != 'django.core.mail.backends.dummy.EmailBackend':

        # Check if we can send email. We just check if the mechanism works, we
        # can not detect if the backend fails after we send it (delayed
        # refusals).
        # noinspection PyBroadException
        try:
            connection = mail.get_connection(fail_silently=False)
            mail.EmailMessage(
                to=['noreply@example.com'],
                subject='Test message',
                body='Test message',
                connection=connection
            ).send(fail_silently=False)
        except:  # Catch all since we do not care about backend at this point
            errors.append(Warning(
                'Can not send email, check your email settings',
                id='deploy_email.W001'
            ))

    # TODO: check spammy-ness of our e-mails
    # TODO: check DEFAULT_FROM_EMAIL, SERVER_EMAIL

    return errors


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_localization(app_configs, **kwargs):
    errors = []

    # TODO: check if translations are available for all languages and warn about missing labels

    return errors


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_logging(app_configs, **kwargs):
    errors = []

    # Get all configs if we don't get a specific set
    if not app_configs:
        app_configs = apps.apps.app_configs.values()

    raven_installed = bool(list(filter(lambda app: app.name == "django.contrib.raven", app_configs)))
    if not raven_installed:
        errors.append(Warning(
            'Raven is not installed',
            id='deploy_logging.W001'
        ))
    else:
        raven_config = getattr(settings, 'RAVEN_CONFIG', None)
        if raven_config is None or not isinstance(raven_config, dict):
            errors.append(Error(
                'Raven config is not set',
                id='deploy_logging.E001'
            ))

        try:
            # noinspection PyPackageRequirements,PyUnresolvedReferences
            from raven.contrib.django.models import client

            # So we are duplicating code from manage.py raven test here...

            if not all([client.servers, client.project, client.public_key, client.secret_key]):
                errors.append(Error(
                    'Raven config is not complete',
                    id='deploy_logging.E002'
                ))

            if not client.is_enabled():
                errors.append(Error(
                    'Raven is disabled',
                    id='deploy_logging.E003'
                ))

            # Test sending
            data = {
                'culprit': 'preflight.checks.check_logging',
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
                    'user': CURRENT_USER,
                    'loadavg': os.getloadavg(),
                },
            ))

            if client.state.did_fail():
                errors.append(Error(
                    'Raven could not send test message',
                    id='deploy_logging.E004'
                ))

        except ImportError:
            print('HUH?')

    # TODO: check logging for email admins if no raven?

    return errors


@register('preflight', deploy=True)
def check_static(app_configs, **kwargs):
    errors = []

    # Get all configs if we don't get a specific set
    if not app_configs:
        app_configs = apps.apps.app_configs.values()

    compressor_installed = bool(list(filter(lambda app: app.name == "compressor", app_configs)))
    if compressor_installed:

        # Check if storage is writeable
        try:
            from compressor.storage import default_storage as storage

            path = storage.save('test', ContentFile('new content'))
        except ImportError:
            print('HUH?')
        except IOError:
            errors.append(Error(
                'Compressor storage is not writeable',
                id='preflight.E003'
            ))
        else:
            storage.delete(path)

        pass
        # TODO: check if compressor is actually compressing?

    return errors


@register('preflight', deploy=True)
def check_templates(app_configs, **kwargs):
    errors = []

    # TODO: check cache headers are set

    if settings.TEMPLATE_DEBUG:
        errors.append(Error(
            'TEMPLATE_DEBUG is still True',
            id='deploy_templates.E001'
        ))

    return errors


#
# External checks
#

@register('preflight', deploy=True)
def check_static_responses(app_configs, **kwargs):
    errors = []

    # TODO: check cache headers are set

    return errors

    # TODO: how to check server settings?