#!/usr/bin/env python -tt
# encoding: utf-8
#
# Created by Holger Rapp on 2009-03-15.
#
# Last Modified: $Date$
#

from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(max_length=200)
    incl_wiki = forms.BooleanField(required=False, initial=True, label='Wiki')
    incl_forum = forms.BooleanField(
        required=False, initial=True, label='Forum')
    incl_news = forms.BooleanField(required=False, initial=True, label='News')
    incl_maps = forms.BooleanField(required=False, initial=True, label='Maps')
    incl_help = forms.BooleanField(
        required=False, initial=True, label='Online Help')
