from django.apps import apps as django_apps
from django.conf import settings

from .app_settings import Settings

app_settings = Settings()


def get_star_ratings_rating_model_name():
    return getattr(settings, "STAR_RATINGS_RATING_MODEL", "star_ratings.Rating")


def get_star_ratings_rating_model():
    return django_apps.get_model(get_star_ratings_rating_model_name())
