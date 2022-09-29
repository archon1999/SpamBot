import os
import whitenoise

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
application = whitenoise.WhiteNoise(application)
application.add_files('static', prefix='static/')
