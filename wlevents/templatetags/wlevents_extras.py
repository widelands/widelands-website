#!/usr/bin/env python
# encoding: utf-8

from wlevents.models import Event
from django import template
from urllib.parse import urlencode, quote

import datetime

register = template.Library()


class GetFutureEvents(template.Node):
    def __init__(self, varname):
        self._vn = varname

    def render(self, context):
        """Only has side effects."""
        context[self._vn] = Event.objects.open()
        return ""


def do_get_future_events(parser, token):
    try:
        tag_name, as_name, variable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "required: %r as <variable name>" % token.contents.split()[0]
        )

    return GetFutureEvents(variable)


register.tag("get_future_events", do_get_future_events)
