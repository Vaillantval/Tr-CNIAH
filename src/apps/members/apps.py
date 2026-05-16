from django.apps import AppConfig


class MembersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.members'

    def ready(self):
        from django.db.models.signals import post_save
        from .models import User
        from . import signals
        post_save.connect(signals.sync_membre_actif, sender=User)
