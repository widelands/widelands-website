from django import forms

from . import app_settings


class RateForm(forms.Form):
    score = forms.IntegerField(min_value=1, max_value=app_settings.STAR_RATINGS_RANGE)
