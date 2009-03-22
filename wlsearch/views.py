# Create your views here.


from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from forms import SearchForm

from wiki.models import Article
from pybb.models import Post, Topic

class DummyEmptyQueryset(object):
    """
    A simple dummy class when a search
    should not be run. The template expects
    a queryset and checks for the count member.
    """
    def count(self):
        return 0

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
         
        if form.is_valid():
            query = form.cleaned_data["search"]
            do_wiki = form.cleaned_data["incl_wiki"]
            do_forum = form.cleaned_data["incl_forum"]
            
            wiki_results = Article.search.query(query) if do_wiki else DummyEmptyQueryset()
            forum_results = Post.search.query(query) if do_forum else DummyEmptyQueryset()
    
            template_params = {
                "wiki_results": wiki_results,
                "forum_results": forum_results,
            }

            return render_to_response("wlsearch/results.html",
                       template_params,
                       context_instance=RequestContext(request))
    else:
        form = SearchForm()

    template_params = {
        "search_form": form,
    }
    return render_to_response("wlsearch/search.html",
                              template_params,
                              context_instance=RequestContext(request))


