# coding: utf8

# Settings for running Omaha from a single server - including the hosting of
# static / media files.

from os.path import pardir, join

import os

from .settings import *

DEBUG = False

ALLOWED_HOSTS = (os.environ.get('HOST_NAME'), '*')
SECRET_KEY = os.environ.get('SECRET_KEY')

CELERYD_HIJACK_ROOT_LOGGER = False

CUP_PEM_KEYS = {
    '1': join(PROJECT_DIR, pardir, 'conf', 'CUP_private.pem')
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.request': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'celery.beat': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}