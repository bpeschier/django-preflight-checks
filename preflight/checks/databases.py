from django.core.checks import register, Warning
from django.conf import settings

W001 = Warning(
    'The default database is a SQLite database',
    id='preflight_database.W001'
)

W002 = Warning(
    """Database connection age (CONN_MAX_AGE) is 0; """
    """you might want to set it to something more persistent.""",
    id='preflight_database.W002'
)

# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_databases(app_configs, **kwargs):
    errors = []

    # Check the default database
    database = settings.DATABASES.get('default')
    if database is not None:
        # We probably do not want SQLite as the default
        if database.get('ENGINE') == 'django.db.backends.sqlite3':
            errors.append(W001)

        # Check connection age
        if database.get('CONN_MAX_AGE') is 0:
            errors.append(W002)

    return errors
