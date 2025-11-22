"""
WSGI config for medi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medi.settings')

application = get_wsgi_application()
<<<<<<< HEAD
app = application
=======
app = application
>>>>>>> 7a2e3ddf6e1640071572fc98b2e3513219667a99
