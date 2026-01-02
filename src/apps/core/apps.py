# src/apps/core/apps.py
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'CNIAH Core'
    
    def ready(self):
        """Import signals when app is ready"""
        # use a relative import so the app's signals module is imported
        # as part of this app package (avoids importing top-level `core`).
        from . import signals  # noqa: F401