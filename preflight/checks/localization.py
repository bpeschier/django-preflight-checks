from django.core.checks import register

# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_localization(app_configs, **kwargs):
    errors = []

    # TODO: check if translations are available for all languages and warn about missing labels

    return errors
