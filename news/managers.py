from django.db.models import Manager
import datetime


class PublicManager(Manager):
    """Returns news posts that are:

       - not in the future
       - not published"""

    def published(self):
        return self.get_queryset().exclude(status=1).filter(publish__lte=datetime.datetime.now())
