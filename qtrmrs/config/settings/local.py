from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]



# Print emails to console instead of sending them (great for dev)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'