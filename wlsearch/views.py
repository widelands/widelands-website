from django.core.urlresolvers import reverse
from django.shortcuts import render
from haystack.generic_views import SearchView
from forms import WlSearchForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from haystack.utils.app_loading import haystack_get_model
from pybb.models import Topic
from pybb.models import Post as ForumPost
from wiki.models import Article
from news.models import Post as NewsPost
from wlmaps.models import Map
from wlhelp.models import Building, Ware, Worker


class HaystackSearchView(SearchView):
    """My custom search view."""
    template_name = 'search/search_test.html'
    form_class = WlSearchForm
    paginate_by = None

    def get(self, request, *args, **kwargs):
        """Used to return form errors."""
        form = self.form_class(request.GET)
        if form.is_valid() and form.cleaned_data['q'] != '':
            context = {'form': form,
                       'query': form.cleaned_data['q'],
                       'result': {}}
            if form.cleaned_data['incl_forum']:
                topic_results = [x for x in form.search(Topic,)]
                post_results = [x for x in form.search(ForumPost)]
                if len(topic_results):
                    context['result'].update({'topics': topic_results})
                if len(post_results):
                    context['result'].update({'posts': post_results})

            if form.cleaned_data['incl_wiki']:
                wiki_results = [x for x in form.search(Article)]
                if len(wiki_results):
                    context['result'].update({'wiki': wiki_results})

            if form.cleaned_data['incl_news']:
                news_results = [x for x in form.search(NewsPost)]
                if len(news_results):
                    context['result'].update({'news': news_results})

            if form.cleaned_data['incl_maps']:
                map_results = [x for x in form.search(Map)]
                if len(map_results):
                    context['result'].update({'maps': map_results})

            if form.cleaned_data['incl_help']:
                worker_results = [x for x in form.search(Worker)]
                ware_results = [x for x in form.search(Ware)]
                building_results = [x for x in form.search(Building)]
                if len(worker_results):
                    context['result'].update({'workers': worker_results})
                if len(ware_results):
                    context['result'].update({'wares': ware_results})
                if len(building_results):
                    context['result'].update({'buildings': building_results})

            return render(request, self.template_name, context)

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """This is executed when searching through the box in the navigation.

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
