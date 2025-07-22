from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # import core.signals.handlers
        if getattr(settings, 'CORE_SIGNALS_ENABLED', True):
            import core.signals.handlers