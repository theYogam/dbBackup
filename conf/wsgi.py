"""
WSGI config for dbbackup project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append('/home/silatchom/Dropbox/PycharmProjects/dbbackup/')

from conf import monitor

monitor.start(interval=1.0)
monitor.track(os.path.join(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()





