#!/usr/bin/env python -tt
# encoding: utf-8

from django import template
from django.contrib.sites.models import Site

import datetime

try:
    from settings import USE_SSL_LOGIN
except ImportError:
    USE_SSL_LOGIN = False

register = template.Library()

class SecureURL(template.Node):
    def __init__(self):
        self.site_name = Site.objects.get(pk=1)
        self.use_ssl = USE_SSL_LOGIN

    def render(self, context):
        if self.use_ssl:
            return "https://%s/accounts/login/" % self.site_name
        return "/accounts/login/"

def secure_login(parser, token):
    return SecureURL()

register.tag("secure_login", secure_login)



