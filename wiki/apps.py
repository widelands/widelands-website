from django.apps import AppConfig
from django.db.models import signals


class WikiConfig(AppConfig):

    name = "wiki"
    verbose_name = "Wiki"

    def ready(self):
        from wiki.management import create_notice_types

        signals.post_migrate.connect(create_notice_types, sender=self)
