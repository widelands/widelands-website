"""Tagging settings with their defaults; the site overrides them in
mainpage/settings.py."""

from django.conf import settings

# The maximum length of a tag's name.
MAX_TAG_LENGTH = getattr(settings, "MAX_TAG_LENGTH", 50)

# Whether to force all tags to lowercase before they are saved to the database.
FORCE_LOWERCASE_TAGS = getattr(settings, "FORCE_LOWERCASE_TAGS", False)
