from django.core.checks import register, Error
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django import apps

E001 = Error(
    'Default storage is not writeable.',
    id='preflight_storages.E001'
)

E002 = Error(
    'Compressor is in INSTALLED_APPS, but the package is not installed.',
    id='preflight_storage.E002'
)

E003 = Error(
    'Compressor storage is not writeable.',
    id='preflight_storage.E003'
)


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_file_storage(app_configs, **kwargs):
    errors = []

    # Check if storage is writeable
    try:
        path = default_storage.save('__test', ContentFile('new content'))
    except IOError:
        errors.append(E001)
    else:
        default_storage.delete(path)

    # TODO: max size, permissions?

    return errors


# noinspection PyUnusedLocal
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
            # noinspection PyPackageRequirements,PyUnresolvedReferences
            from compressor.storage import default_storage as storage

            path = storage.save('test', ContentFile('new content'))
        except ImportError:
            errors.append(E002)
        except IOError:
            errors.append(E003)
        else:
            storage.delete(path)

        pass
        # TODO: check if compressor is actually compressing?

    return errors
