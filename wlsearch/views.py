from django.core.urlresolvers import reverse
from django.shortcuts import render
from haystack.generic_views import SearchView
from forms import WlSearchForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from datetime import date, timedelta


class HaystackSearchView(SearchView):
    """My custom search view."""
    template_name = 'search/search_test.html'
    form_class = WlSearchForm
    paginate_by = None


    def get(self, request, *args, **kwargs):
        """Used to return form errors"""
        form = self.form_class(request.GET)
        if form.is_valid():
            form.search()
            return super(HaystackSearchView, self).get(form)
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """ This is executed when searching through the box in the navigation
        
        We build the query string and redirect it to this view again.
    
        """
        form = self.form_class(request.POST)
        if form.is_valid() and form.cleaned_data['q'] != '':
            print('franku cleaned_data: ',form.cleaned_data)
            # Allways set the search string
            search_url = 'q=%s' % (form.cleaned_data['q'])
            # add initial values of the form fields
            for field, v in form.fields.iteritems():
                if field =='q':
                    continue
                search_url += '&%s=%s' % (field, v.initial)
            return HttpResponseRedirect('%s?%s' % (reverse('search'), search_url))
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def get_context_data(self, *args, **kwargs):
        """ Regrouping the search results """
    
        context = super(HaystackSearchView, self).get_context_data(*args, **kwargs)
        maps = []
        topics = []
        posts = []
        workers = []
        for item in context['object_list']:
            #print('franku item: ', item)
            if item.content_type() == 'wlmaps.map':
                maps.append(item)
            if item.content_type() == "pybb.post":
                posts.append(item)
            if item.content_type() == "pybb.topic":
                topics.append(item)
            if item.content_type() == "wlhelp.worker":
                workers.append(item)
        
        sorted_objects = [
            {'maps': maps},
            {'topics': topics},
            {'posts': posts},
            {'workers': workers},
        ]
        context['object_list'] = sorted_objects
        
        return context
