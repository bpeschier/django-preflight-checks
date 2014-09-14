from django.core.checks import register, Error
from django.conf import settings

E001 = Error(
    'TEMPLATE_DEBUG is still True',
    id='preflight_templates.E001'
)


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_templates(app_configs, **kwargs):
    errors = []

    # TODO: check cache headers are set

    if settings.TEMPLATE_DEBUG:
        errors.append(E001)

    return errors
