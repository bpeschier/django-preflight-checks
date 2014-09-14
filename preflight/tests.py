import django
from django import apps
from django.test import SimpleTestCase
from django.test.utils import override_settings, modify_settings
from django.conf import settings
from checks import caches, databases, debug, email, external, localization, logging, preflight, storages, templates

settings.configure(DEBUG=False)
django.setup()


class PreflightTests(SimpleTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apps = apps.apps.app_configs.values()

    #
    # Caches
    #

    @override_settings(CACHES={})
    def test_caches_nocache(self):
        self.assertListEqual([], caches.check_caches(self.apps))

    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
    def test_caches(self):
        self.assertIn(caches.E001, caches.check_caches(self.apps))

    #
    # Databases
    #

    @override_settings(DATABASES={})
    def test_databases_nodatabase(self):
        self.assertListEqual([], databases.check_databases(self.apps))

    @override_settings(DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'CONN_MAX_AGE': 0}})
    def test_databases(self):
        self.assertListEqual(
            [databases.W001, databases.W002],
            databases.check_databases(self.apps)
        )

    #
    # Debug
    #

    @override_settings(DEBUG_PROPAGATE_EXCEPTIONS=True)
    def test_debug(self):
        self.assertListEqual([debug.E001], debug.check_debug(self.apps))

    @modify_settings(INSTALLED_APPS={'append': 'debug_toolbar'})
    def test_debug_toolbar(self):
        self.assertListEqual(
            [debug.W001],
            debug.check_debug(self.apps)
        )

    @modify_settings(INSTALLED_APPS={'append': 'debug_toolbar'})
    @override_settings(DEBUG_TOOLBAR_PATCH_SETTINGS=True)
    def test_debug_toolbar_override(self):
        django.setup()
        self.assertListEqual(
            [debug.W001, debug.W002],
            debug.check_debug(self.apps)
        )
