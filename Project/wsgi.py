"""
WSGI config for Project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import sys
import djcelery
from django.core.wsgi import get_wsgi_application


djcelery.setup_loader()

sys.path.append('/opt/bitnami/apps/django/django_projects/Project')
os.environ.setdefault(
    "PYTHON_EGG_CACHE", "/opt/bitnami/apps/django/django_projects/Project/egg_cache")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')

application = get_wsgi_application()
