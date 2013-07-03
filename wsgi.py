import os, sys

sys.path.append(os.path.dirname(__file__))

import django.conf
django.conf.ENVIRONMENT_VARIABLE = "DJANGO_FINANCE_SETTINGS_MODULE"
os.environ.setdefault("DJANGO_FINANCE_SETTINGS_MODULE", "finance.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
