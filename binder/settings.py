# Django settings for binder project.
import logging
import os
from cryptography.fernet import Fernet
from django.contrib.messages import constants as messages

logger = logging.getLogger(__name__)

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
DEBUG = True
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

ALLOWED_HOSTS=['*']

DB_NAME = os.environ.get('DJANGO_DB_NAME', 'binder')
DB_USER = os.environ.get('DJANGO_DB_USER', None)
DB_PASSWORD = os.environ.get('DJANGO_DB_PASSWORD', None)
DB_HOST = os.environ.get('DJANGO_DB_HOST', None)

if all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST]):
    logger.info("Using MySQL server for data backend.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': 3306,
        }
    }
else:
    logger.info("Using Sqlite database at %s" % (os.path.join(SITE_ROOT, 'db') + '/binder.db'))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(SITE_ROOT, 'db') + '/binder.db',
        }
    }

TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(SITE_ROOT, "files")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/files/"
STATIC_URL= "/static/"

SECRET_FILE = os.path.join(SITE_ROOT, 'secret.txt')
try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except IOError:
    try:
        from random import choice
        SECRET_KEY = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
        secret = open(SECRET_FILE, 'w')
        secret.write(SECRET_KEY)
        secret.close()
    except IOError:
        Exception('Please create a %s file with random characters to generate your secret key!' % SECRET_FILE)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': os.path.join(SITE_ROOT, "templates"),
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages'
                ],
            'debug': True
            }
    }
]

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'binder.middlewares.LoginRequiredMiddleware',
)

ROOT_URLCONF = 'binder.urls'

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'binder',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO'
        },
        'binder': {
            'handlers': ['console'],
            'level': 'DEBUG'
        }
    }
}

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

TTL_CHOICES = ((300, "5 minutes"),
               (1800, "30 minutes"),
               (3600, "1 hour"),
               (43200, "12 hours"),
               (86400, "1 day"))

RECORD_TYPE_CHOICES = (("A", "A"),
                       ("AAAA", "AAAA"),
                       ("CNAME", "CNAME"))

LOGIN_REDIRECT_URL = '/'

# TSIG Encryption Key
# If not passed as an environment variable,
# create a new Fernet key for encrypting the TSIG key.

# NOTE: In production, you'll want to pass your own key in.
# Otherwise, on successive Binder restarts, you will not be able
# to decrypt your TSIG Key and perform DNS updates because the keys
# would have changed.
FERNET_KEY=os.environ.get("DJANGO_FERNET_KEY", Fernet.generate_key())

try:
    from local_settings import *
except ImportError:
    pass


# Base directory where credentials are to be stored.
# For NSD, a subdirectory under CREDS_DIR should be created with th e
# appropriate certificates for nsd-control to execute.
CREDS_DIR = "/creds"
