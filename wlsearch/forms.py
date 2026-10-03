from django import forms
from datetime import date, timedelta


class WlSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={"type": "search"}),
    )
    start_date = forms.DateField(
        required=False,
        initial=date.today() - timedelta(365),
        widget=forms.TextInput(
            attrs={
                "size": "10",
                "placeholder": "YYYY-MM-DD",
                "class": "datepicker",
            }
        ),
    )
    incl_forum = forms.BooleanField(required=False, initial=True, label="Forum")
    incl_maps = forms.BooleanField(required=False, initial=True, label="Maps")
    incl_wiki = forms.BooleanField(required=False, initial=True, label="Wiki")
    incl_help = forms.BooleanField(required=False, initial=True, label="Encyclopedia")
    incl_news = forms.BooleanField(required=False, initial=True, label="News")
