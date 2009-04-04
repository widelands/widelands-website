#!/usr/bin/env python -tt
# encoding: utf-8

from django import forms

class UploadMapForm(forms.Form):
    mapfile = forms.FileField()

