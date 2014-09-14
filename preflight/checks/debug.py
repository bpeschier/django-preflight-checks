from django.core.checks import register, Error, Warning
from django.conf import settings
from django import apps


E001 = Error(
    'DEBUG_PROPAGATE_EXCEPTIONS is still True.',
    id='preflight_debug.E001'
)

W001 = Warning(
    'Debug toolbar is installed.',
    id='preflight_debug.W001'
)

W002 = Warning(
    'Debug toolbar is activated.',
    id='preflight_debug.W002'
)

# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_debug(app_configs, **kwargs):
    errors = []

    if settings.DEBUG_PROPAGATE_EXCEPTIONS:
        errors.append(E001)

    # Get all configs if we don't get a specific set
    if not app_configs:
        app_configs = apps.apps.app_configs.values()

    # Check for debug toolbar
    debug_toolbar = list(filter(lambda app: app.name == "debug_toolbar", app_configs))
    if debug_toolbar:
        errors.append(W001)

        if hasattr(settings, 'DEBUG_TOOLBAR_PATCH_SETTINGS') and settings.DEBUG_TOOLBAR_PATCH_SETTINGS:
            errors.append(W002)

    return errors
