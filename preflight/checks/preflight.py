import pwd
import os

from django.core.checks import register, Warning
from django.conf import settings

#
# Internal checks
#

W001 = Warning(
    'No DEPLOY_TARGET_USER set, define it to check write permissions on storages.',
    id='preflight.W001'
)

W002 = Warning(
    'You are not running as DEPLOY_TARGET_USER, writeable-checks can not be trusted.',
    id='preflight.W002'
)


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_user(app_configs, **kwargs):
    errors = []

    current_user = pwd.getpwuid(os.getuid()).pw_name
    target_user = getattr(settings, 'DEPLOY_TARGET_USER', None)

    if target_user is None:
        errors.append(W001)

    if target_user and target_user != current_user:
        errors.append(W002)

    return errors
