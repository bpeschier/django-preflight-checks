from django.core.checks import register


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_static_responses(app_configs, **kwargs):
    errors = []

    # TODO: check cache headers are set

    return errors

    # TODO: how to check server settings?
