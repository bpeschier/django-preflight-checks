from django.conf import settings
from django import apps
from django.core.checks import register, Error, Warning
from django.core.files.base import ContentFile

E001 = Error(
    'django-compressor is in INSTALLED_APPS, but the package is not installed.',
    id='preflight_static.E001'
)

E002 = Error(
    'django-compressor storage is not writeable.',
    id='preflight_static.E002'
)

E003 = Error(
    'django-compressor is disabled (COMPRESS_ENABLED).',
    id='preflight_static.E003'
)

E004 = Error(
    'The compressor debug toggle is still enabled (COMPRESS_DEBUG_TOGGLE).',
    id='preflight_static.E004'
)

W001 = Warning(
    'django-compressor is not installed.',
    id='preflight_static.W001'
)


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_compressor(app_configs, **kwargs):
    errors = []

    # Get all configs if we don't get a specific set
    if not app_configs:
        app_configs = apps.apps.app_configs.values()

    compressor_installed = bool(list(filter(lambda app: app.name == "compressor", app_configs)))
    if not compressor_installed:
        errors.append(W001)
    else:

        # Check if storage is writeable
        try:
            # noinspection PyPackageRequirements,PyUnresolvedReferences
            from compressor.storage import default_storage as storage

            path = storage.save('test', ContentFile('new content'))
        except ImportError:
            errors.append(E001)
        except IOError:
            errors.append(E002)
        else:
            storage.delete(path)

        if not getattr(settings, 'COMPRESS_ENABLED'):
            errors.append(E003)

        if getattr(settings, 'COMPRESS_DEBUG_TOGGLE'):
            errors.append(E004)

    return errors
