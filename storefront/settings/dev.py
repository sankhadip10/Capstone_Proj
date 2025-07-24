from .common import *

DEBUG = True

# Use environment variable for secret key with fallback
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production-abc123xyz789')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '713e64d060b2.ngrok-free.app']

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront3',
        # 'HOST': 'mysql',
        'HOST': os.environ.get('MYSQL_HOST', 'localhost'),
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
        "LOCATION": os.environ.get('CACHE_URL', 'redis://localhost:6379/2'),
        "TIMEOUT": 10 * 60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# EMAIL_HOST = 'smtp4dev'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
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
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET', '')


