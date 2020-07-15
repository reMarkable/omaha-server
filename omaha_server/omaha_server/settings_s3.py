# coding: utf8

# Settings for running Omaha with Sentry and static / media files on S3.
# This requires you to set some environment variables. See .bashrc.

from os.path import pardir, join

import os

from .settings_prod import *

AWS_S3_HOST = os.environ.get('AWS_S3_HOST')

# Host static files (CSS etc.) from the server. No point in doing it from S3.
# In particular, this ensures that `collectstatic` takes seconds, not minutes,
# when setting up the server.
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_URL = '/static/'

# Mimic reMarkable's original setup. Later, we may want to restrict to just one
# server here.
ALLOWED_HOSTS = ['*']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

if CUP_REQUEST_VALIDATION:
	CUP_PEM_KEYS = {
		'1': join(PROJECT_DIR, pardir, 'conf', 'CUP_private.pem')
	}