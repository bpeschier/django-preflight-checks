from django.core.checks import register, Error
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

E001 = Error(
    'Default storage is not writeable.',
    id='preflight_storages.E001'
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
