"""
WSGI config for HSReplay.net

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application


sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hsreplaynet.settings")

application = get_wsgi_application()

try:
	from whitenoise.django import DjangoWhiteNoise
	application = DjangoWhiteNoise(application)
except ImportError as e:
	sys.stderr.write("Not running with Whitenoise (%s)\n" % (e))
