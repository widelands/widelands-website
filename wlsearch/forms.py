from haystack.forms import SearchForm
from django import forms
from datetime import date, timedelta
from haystack.query import SearchQuerySet


class WlSearchForm(SearchForm):
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

    def search(self, search_models):
        """Search per model"""

        sqs = SearchQuerySet().models(search_models)

        # Add start_date to the query
        if self.cleaned_data["start_date"]:
            sqs = sqs.filter(date__gte=self.cleaned_data["start_date"])

        # Add Order to the query
        sqs = sqs.order_by("-date")

        # Run the query
        result = sqs.auto_query(self.cleaned_data["q"]).load_all()

        return result
