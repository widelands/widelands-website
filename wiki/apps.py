from django.apps import AppConfig
from django.db.models import signals


class WikiConfig(AppConfig):
    
    name = 'wiki'
    verbose_name = 'The widelands wiki'
    
    def ready(self):
        from wiki.management import create_notice_types
        from notification import models as notification
        print("trying to ")
        signals.post_migrate.connect(create_notice_types, sender=notification)
