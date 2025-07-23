# storefront/settings/test.py
from .dev import *

# Test-specific settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront3',
        'HOST': os.environ.get('MYSQL_HOST', 'mysql'),  # Use Docker MySQL
        'USER': 'root',
        'PASSWORD': 'P@ssword',
        'TEST': {
            'NAME': 'test_storefront3',  # Test database name
        }
    }
}

# Disable signal in test settings
CORE_SIGNALS_ENABLED = False

# Use in-memory cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['null'],
        },
    },
}

# Use console email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'