=========
Preflight
=========

Preflight is a set of deploy checks for Django 1.8 and higher which inspect 
your settings and setup for common configuration errors on production 
environments. Often these are flags which are disabled during development 
(``DEBUG = True``) and can easily be overlooked before going live.

Built-in checks cover inspections for non-production settings in caches, 
databases, email, logging, storages, templates and more. They are 
opinionated, either for "common" packages (raven, django-compressor, ...) or 
(in our eyes) optimal configurations, but Django's check framework lets you 
silence the ones you do not need.


Installation
============

Run ``pip install git+https://github.com/bpeschier/django-preflight-checks.git``.

Add ``preflight`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        ...
        'preflight',
    )


Running checks 
==============

Checks are part of the Django deploy checks, you can run them with::

    python manage.py check --deploy

