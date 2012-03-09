# This file specifies needed environment and configuration
# data for the Binder app to operate under mod_wsgi.

import os
import sys

PROJECT_PATH=os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, "binder"))

os.environ['DJANGO_SETTINGS_MODULE'] = 'binder.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
