from django.apps import AppConfig
from django.db.models import signals


class PybbConfig(AppConfig):
    name = "pybb"
    verbose_name = "Pybb"

    def ready(self):
        from pybb.management.pybb_notifications import create_notice_types

        signals.post_migrate.connect(create_notice_types, sender=self)
