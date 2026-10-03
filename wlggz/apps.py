from django.apps import AppConfig


class WlGGZConfig(AppConfig):
    name = "wlggz"

    def ready(self):
        from . import signals  # noqa: F401
