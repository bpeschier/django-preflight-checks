from django.core.checks import register, Error
from django.conf import settings

E001 = Error(
    'The cache backend is still set to local memory, install a real cache or set it to dummy.',
    id='preflight_cache.E001'
)

# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_caches(app_configs, **kwargs):
    errors = []

    # Check for local memory cache
    cache = settings.CACHES.get('default')
    if cache is not None:
        if cache.get('BACKEND') == 'django.core.cache.backends.locmem.LocMemCache':
            errors.append(E001)

    return errors
