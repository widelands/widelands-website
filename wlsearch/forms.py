from haystack.forms import SearchForm
from haystack.utils.app_loading import haystack_get_model
from django import forms
from datetime import date, timedelta


class WlSearchForm(SearchForm):

    start_date = forms.DateField(
        required=False, initial=date.today() - timedelta(365*2),
        widget=forms.TextInput(attrs=
                               {'size': '10',
                                #'placeholder': 'YYYY-MM-DD',
                                'class': 'datepicker',
                                }))
    incl_forum = forms.BooleanField(
        required=False, initial=True, label='Forum')
    incl_maps = forms.BooleanField(
        required=False, initial=True, label='Maps')
    incl_wiki = forms.BooleanField(
        required=False, initial=True, label='Wiki')
    incl_help = forms.BooleanField(
        required=False, initial=True, label='Encyclopedia')
    incl_news = forms.BooleanField(
        required=False, initial=True, label='News')

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(WlSearchForm, self).search()

        # Collect the models to search for
        search_models = []
        if self.cleaned_data['incl_forum']:
            search_models.append(haystack_get_model('pybb', 'topic'))
            search_models.append(haystack_get_model('pybb', 'post'))
        if self.cleaned_data['incl_maps']:
            search_models.append(haystack_get_model('wlmaps', 'map'))
        # if self.cleaned_data['incl_wiki']:
        #     search_models.append(haystack_get_model('wiki', 'article'))
        if self.cleaned_data['incl_help']:
            search_models.append(haystack_get_model('wlhelp', 'worker'))
            search_models.append(haystack_get_model('wlhelp', 'tribe'))
            search_models.append(haystack_get_model('wlhelp', 'ware'))
            search_models.append(haystack_get_model('wlhelp', 'building'))
        # if self.cleaned_data['incl_news']:
        #     search_models.append(haystack_get_model('news', 'post'))
        # Add the chosen models to the query
        if search_models:
            sqs = sqs.models(*search_models)

        # Check to see if a start_date was chosen.
        if self.cleaned_data['start_date']:
            sqs = sqs.filter(date__gte=self.cleaned_data[
                             'start_date'])
        # Order by date
        sqs = sqs.order_by('-date')
        
        # Run the query
        return sqs
