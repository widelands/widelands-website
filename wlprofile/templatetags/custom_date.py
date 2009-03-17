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

from django.utils.translation import ugettext as _
from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.template.defaultfilters import date as django_date

import re
import datetime

register = template.Library()


natural_day_expr =  re.compile(r'''\%ND\((.*?)\)''')
natural_year_expr =  re.compile(r'''\%NY\((.*?)\)''')

def do_custom_date( format, date, now= None ):
    """
    Returns a string formatted representation of date according to format. This accepts
    all formats that strftime also accepts, but it also accepts some new options which are dependant
    on the current date.
        %NY(format)        (natural year) for example %NY(.%Y) will give ".2008" if this year is not 2008, else 
                            an empty string
        %ND(alternatives)  (natural day) for example %ND(%d.%m.%Y) 
        -> Yields today, yesterday, tomorrow or 2.12.2008
    
    format - format string as described above
    date   - datetime object to display
    now    - overwrite the value for now; only for debug reasons 
    """
    if now is None:
        now = datetime.datetime.now()
        
    def _replace_ny(g):
        if now.year == date.year:
            return ""
        return g.group(1)
    
    def _replace_nd(g):
        delta = datetime.date(date.year,date.month,date.day) - \
                datetime.date(now.year,now.month,now.day)
        if delta.days == 0:
            return _(ur'\t\o\d\a\y')
        elif delta.days == 1:
            return _(ur'\t\o\m\o\r\r\o\w')
        elif delta.days == -1:
            return _(ur'\y\e\s\t\e\r\d\a\y')
        else:
            return g.group(1)
    try:
        while 1:
            oformat = format
            format = natural_year_expr.sub(_replace_ny,format)
            format = natural_day_expr.sub(_replace_nd,format)
            if oformat == format:
                break
        
        data = django_date(date,format)
    except NotImplementedError:
        return format

    return data

@register.filter
def custom_date( date, user ):
    """
    If this user is logged in, return his representation, 
    otherwise, return a sane default
    """
    if user.is_anonymous():
        return django_date("j F Y", date)
    return do_custom_date( user.get_profile().time_display, date )
custom_date.is_safe = False
