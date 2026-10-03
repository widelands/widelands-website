from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TaggingConfig(AppConfig):
    name = "tagging"
    label = "tagging"
    verbose_name = _("Tagging")
