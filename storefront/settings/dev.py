from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SECRET_KEY = 'django-insecure-uv+#w-4ck2lf177lu62%gz&zt5gmpb#*8k#anpyu$w8a+go4()'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '713e64d060b2.ngrok-free.app']

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront3',
        # 'HOST': 'mysql',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'P@ssword'
    }
}

# CELERY_BROKER_URL = 'redis://redis:6379/1'
CELERY_BROKER_URL = 'redis://localhost:6379/1'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # "LOCATION": "redis://redis:6379/2",
        "LOCATION": "redis://localhost:6379/2",
        "TIMEOUT": 10 * 60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# EMAIL_HOST = 'smtp4dev'
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 2525

# (sends emails to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBARL_CALLBACK': lambda request: True,
}

# to fix the silk warning
SILKY_PYTHON_PROFILER = True

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'djoser': {'handlers': ['console'], 'level': 'DEBUG'},
    },
}

# Razorpay Test Keys (get from Razorpay Dashboard)
RAZORPAY_KEY_ID = 'rzp_test_GLpdkglq1xc3ql'
RAZORPAY_KEY_SECRET = 'RuqJDjQUIn3fDoN7dP5EFbtw'
RAZORPAY_WEBHOOK_SECRET = 'razorpay_test_secret_123'


