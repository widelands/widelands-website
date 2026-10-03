from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


def calculate_ratings(sender, instance, **kwargs):
    instance.rating.calculate()


class StarRatingsAppConfig(AppConfig):
    name = "star_ratings"

    def ready(self):
        from .models import UserRating

        post_save.connect(calculate_ratings, sender=UserRating)
        post_delete.connect(calculate_ratings, sender=UserRating)
