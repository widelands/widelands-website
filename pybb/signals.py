from django.db.models.signals import post_save
from django.contrib.auth.models import User

from pybb.models import Post


def post_saved(instance, **kwargs):
    pass
    # notify_topic_subscribers(instance)


def setup_signals():
    post_save.connect(post_saved, sender=Post)
