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

from haystack.forms import ModelSearchForm
import datetime

class WlSearchForm(ModelSearchForm):
    
    start_date = forms.DateField(widget=forms.TextInput(attrs={'size': '10', 'placeholder':'YYYY-MM-DD'}), required=False)
    
    def search(self):      
        #First, store the SearchQuerySet received from other processing.
        sqs = super(WlSearchForm, self).search()
    
        if not self.is_valid():
            return self.no_query_found()

        print('is valid', self.cleaned_data)

        # Check to see if a start_date was chosen.
        if self.cleaned_data['start_date']:
            print('franku start_date: ', self.cleaned_data['start_date'])
            sqs = sqs.filter(date__gte=self.cleaned_data['start_date']).order_by('-date')
    
        return sqs
