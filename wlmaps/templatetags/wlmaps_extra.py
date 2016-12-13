#!/usr/bin/env python -tt
# encoding: utf-8

from django import template

register = template.Library()


@register.filter
def average_rating(rating):
    if rating.votes > 0:
        avg = '%.1f' % (float(rating.score) / rating.votes)
    else:
        avg = '0.0'
    return avg
