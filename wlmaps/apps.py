from django.apps import AppConfig
from django.db.models import signals


class WlMapsConfig(AppConfig):

    name = 'wlmaps'
    verbose_name = 'Widelands Maps'

    def ready(self):
        from wlmaps.management import create_notice_types
        signals.post_migrate.connect(create_notice_types, sender=self)

