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
        """Used to return form errors."""
        form = self.form_class(request.GET)
        if form.is_valid():
            form.search()
            return super(HaystackSearchView, self).get(form)

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """ This is executed when searching through the box in the navigation.

        We build the query string and redirect it to this view again.

        """
        form = self.form_class(request.POST)
        if form.is_valid() and form.cleaned_data['q'] != '':
            # Allways set the search string
            search_url = 'q=%s' % (form.cleaned_data['q'])
            # add initial values of the form fields
            for field, v in form.fields.iteritems():
                if field == 'q':
                    continue
                search_url += '&%s=%s' % (field, v.initial)
            return HttpResponseRedirect('%s?%s' % (reverse('search'), search_url))
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def get_context_data(self, *args, **kwargs):
        """Regrouping the search results."""

        context = super(HaystackSearchView, self).get_context_data(
            *args, **kwargs)
        
        maps = [m for m in context['object_list'] if m.content_type() == "wlmaps.map"]
        topics = [t for t in context['object_list'] if t.content_type() == "pybb.topic"]
        posts = [p for p in context['object_list'] if p.content_type() == "pybb.post"]
        workers = [w for w in context['object_list'] if w.content_type() == "wlhelp.worker"]
        buildings = [b for b in context['object_list'] if b.content_type() == "wlhelp.building"]
        wares = [w for w in context['object_list'] if w.content_type() == "wlhelp.ware"]
        tribes = [t for t in context['object_list'] if t.content_type() == "wlhelp.tribe"]

        sorted_objects = []
        # Put all found things into the context, omit if nothing was found
        # so the context is as small as possible
        if len(maps) > 0 :
            sorted_objects.append({'wlmaps': {'maps': maps}})
        if len(topics) > 0 or len(posts) > 0:
            sorted_objects.append({'forum': {'topics': topics,
                       'posts': posts,
                       }},)
        if len(workers) or len(buildings) or len(wares) or len(tribes):
            sorted_objects.append({'encyclopedia': {'wares': wares,
                              'buildings': buildings,
                              'tribes': tribes,
                              'workers': workers,
                              }})

        context['object_list'] = sorted_objects
        
        return context
