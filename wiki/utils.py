# -*- coding: utf-8 -*-
""" Some util functions.
"""
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


def get_ct(obj):
    """ Return the ContentType of the object's model.
    """
    return ContentType.objects.get(app_label=obj._meta.app_label,
                                   model=obj._meta.module_name)

