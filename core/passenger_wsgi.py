"""
WSGI config for HelloDjango project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os, sys

site_user_root_dir = '/home/v/vpe1ya/smm/public_html'
# sys.path.insert(1, os.path.join(site_user_root_dir, 'venv/lib/python3.6/site-packages'))
sys.path.insert(0, os.path.join(site_user_root_dir, 'Project'))
sys.path.insert(1, '/home/v/vpe1ya/.local/lib/python3.7/site-packages')

from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()


