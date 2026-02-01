#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: wlprofile/templatetags/wlprofile.py
#
# Created by Holger Rapp on 2009-03-15.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

from django.utils.translation import gettext as _
from django import template
from django.template.defaultfilters import date as django_date
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
import re
from datetime import date as ddate, tzinfo, timedelta, datetime
from django.conf import settings
from zoneinfo import ZoneInfo


register = template.Library()


natural_day_expr = re.compile(r"""\%ND\((.*?)\)""")
natural_year_expr = re.compile(r"""\%NY\((.*?)\)""")

ZERO = timedelta(0)
HOUR = timedelta(hours=1)


def make_aware_date(date):
    """We are currently store only "naive" date objects, that are objects with no timezone
    information. But we are using the current servertime for storing the dates for
    objects.
    Make the naive date an aware date by assigning the time zone of the server."""

    if date.tzinfo is None:
        return date.replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
    return date


class FixedOffset(tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name):
        self.__offset = timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO


def do_custom_date(format, date, tz_offset=1.0, now=None):
    """Returns a string formatted representation of date according to format.
    This accepts all formats that strftime also accepts, but it also accepts
    some new options which are dependant on the current date.

        %NY(format)        (natural year) for example %NY(.%Y) will give ".2008" if this year is not 2008, else
                            an empty string
        %ND(alternatives)  (natural day) for example %ND(%d.%m.%Y)
        -> Yields today, yesterday, tomorrow or 2.12.2008

    format      - format string as described above
    date        - datetime object to display
    tz_offset   - the offset from UTC
    now         - overwrite the value for now; only for debug reasons

    """

    ############################
    # Set Timezone Information's
    #
    # set the timezone named info
    if tz_offset > 0:
        tz_info = "UTC+" + str(tz_offset)
    elif tz_offset < 0:
        tz_info = "UTC" + str(tz_offset)
    else:
        tz_info = "UTC"

    # set the user's timezone information
    ForumUserTimeZone = FixedOffset(tz_offset * 60, tz_info)

    if now is None:
        # We need the users local time for comparison
        now = datetime.now(tz=ForumUserTimeZone)

    try:
        # If date is naive (no timezone), treat it as UTC+1 for backward compatibility
        # This matches the original behavior where naive datetimes were assumed to be
        # in Europe/Berlin standard time (UTC+1, not considering DST)
        if date.tzinfo is None:
            utc_plus_one = FixedOffset(60, "UTC+1")
            date = date.replace(tzinfo=utc_plus_one)
        date = date.astimezone(ForumUserTimeZone)
    except AttributeError:  # maybe this is no valid date object?
        return format

    # If it's done, timezone informations are now available ;)
    ############################

    def _replace_ny(g):
        if now.year == date.year:
            return ""
        return g.group(1)

    def _replace_nd(g):
        delta = ddate(date.year, date.month, date.day) - ddate(
            now.year, now.month, now.day
        )
        if delta.days == 0:
            return _(r"\T\o\d\a\y")
        elif delta.days == 1:
            return _(r"\T\o\m\o\r\r\o\w")
        elif delta.days == -1:
            return _(r"\Y\e\s\t\e\r\d\a\y")
        else:
            return g.group(1)

    try:
        while 1:
            oformat = format
            format = natural_year_expr.sub(_replace_ny, format)
            format = natural_day_expr.sub(_replace_nd, format)
            if oformat == format:
                break
        data = django_date(date, format)
    except NotImplementedError:
        return format
    return data


@register.filter
def custom_date(date, user):
    """If this user is logged in, return his representation, otherwise, return
    a sane default.
    """

    def _get_offset(date):
        # Return the utc-offset depending whether if the date is UTC+1 or UTC+2
        return date.utcoffset().seconds / 60 / 60

    if not isinstance(date, datetime):
        return date

    # Add timezone information
    date = make_aware_date(date)

    if not user.is_authenticated:
        return do_custom_date(
            settings.DEFAULT_TIME_DISPLAY,
            date,
            tz_offset=_get_offset(date),
        )
    try:
        userprofile = User.objects.get(username=user).wlprofile
        return do_custom_date(
            userprofile.time_display, date, tz_offset=userprofile.time_zone
        )
    except ObjectDoesNotExist:
        return do_custom_date(
            settings.DEFAULT_TIME_DISPLAY, date, tz_offset=_get_offset(date)
        )


custom_date.is_safe = False


def pluralize(value, name):
    """Pluralize a name.

    Depending on 'value', the 'name' will be pluralized or not. Negative
    values get a minus sign.
    """

    if value > 1:
        return f"{value:-.0f} {name}s"

    return f"{value:-.0f} {name}"


@register.filter
def elapsed_time(date):
    """Calculate elapsed time.

    Returns either minutes, hours or days
    """

    today = datetime.today()
    seconds = (today - date).total_seconds()

    # Python3: Operator '//' = floor division (result is rounded down)
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    if hours == 0 and minutes <= 1:
        return pluralize(1, "minute")
    elif hours == 0:
        return pluralize(minutes, "minute")
    elif hours == 1 or days == 0:
        return pluralize(hours, "hour")
    else:
        return pluralize(days, "day")

    return "Failure"


@register.simple_tag
def current_time(user):
    time = datetime.today()
    time = custom_date(time, user)
    return time


@register.filter
def sec_since_epoch(date):
    """Return seconds since epoch and make sure we have the correct timezone attached."""
    date = make_aware_date(date)
    return date.timestamp()
