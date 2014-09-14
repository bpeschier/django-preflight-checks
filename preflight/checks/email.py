from django.core.checks import register, Error, Warning, Info
from django.core import mail
from django.conf import settings

E001 = Error(
    'EMAIL_BACKEND is set to a testing/debug backend.',
    id='preflight_email.E001'
)

E002 = Error(
    "DEFAULT_FROM_EMAIL is set to an @localhost address.",
    id='preflight_email.E002'
)

W001 = Warning(
    'Can not send email, check your email settings.',
    id='preflight_email.W001'
)

I001 = Info(
    "SERVER_EMAIL is still set to 'root@localhost'.",
    id='preflight_email.I001'
)


# noinspection PyUnusedLocal
@register('preflight', deploy=True)
def check_email(app_configs, **kwargs):
    errors = []

    # Check for debug-ish email backends
    if settings.EMAIL_BACKEND in [
        'django.core.mail.backends.console.EmailBackend',
        'django.core.mail.backends.filebased.EmailBackend',
        'django.core.mail.backends.locmem.EmailBackend',
    ]:
        errors.append(E001)

    # So we assume if you set the dummy backend, you are not interested in mail,
    # otherwise you would have used on of the other ones to actually see mails
    # being sent.
    if settings.EMAIL_BACKEND != 'django.core.mail.backends.dummy.EmailBackend':

        # Check if we can send email. We just check if the mechanism works, we
        # can not detect if the backend fails after we send it (delayed
        # refusals).
        # noinspection PyBroadException
        try:
            connection = mail.get_connection(fail_silently=False)
            mail.EmailMessage(
                to=['noreply@example.com'],
                subject='Test message',
                body='Test message',
                connection=connection
            ).send(fail_silently=False)
        except:  # Catch all since we do not care about backend at this point
            errors.append(W001)

        if settings.DEFAULT_FROM_EMAIL.endswith('@localhost'):
            errors.append(E002)

        if settings.SERVER_EMAIL == 'root@localhost':
            errors.append(I001)

    # TODO: check spammy-ness of our e-mails

    return errors
