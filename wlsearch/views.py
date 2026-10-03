from django.core.paginator import InvalidPage, Page, Paginator
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import WlSearchForm
from pybb.models import Topic
from pybb.models import Post as ForumPost
from wiki.models import Article
from news.models import Post as NewsPost
from wlmaps.models import Map
from wlhelp.models import Building, Ware, Worker

choices = {
    "Forum": "incl_forum",
    "Encyclopedia": "incl_help",
    "Wiki": "incl_wiki",
    "News": "incl_news",
    "Maps": "incl_maps",
}

RESULTS_PER_PAGE = 50

# The result lists shown for each section checkbox of the search form
sections = {
    "incl_forum": {"topics": Topic, "posts": ForumPost},
    "incl_wiki": {"wiki": Article},
    "incl_news": {"news": NewsPost},
    "incl_maps": {"maps": Map},
    "incl_help": {"workers": Worker, "wares": Ware, "buildings": Building},
}


def _results_page(search_query_set, number):
    """Return the requested page of search results, or None if it does not
    exist.

    Paginator.page() shortens the slice of the last page, which the Whoosh
    backend maps to the wrong offset, so always slice whole pages.
    """
    paginator = Paginator(search_query_set, RESULTS_PER_PAGE)
    try:
        number = paginator.validate_number(number)
    except InvalidPage:
        return None
    bottom = (number - 1) * RESULTS_PER_PAGE
    return Page(search_query_set[bottom : bottom + RESULTS_PER_PAGE], number, paginator)


def search(request):
    """Custom search view."""

    if request.method == "POST":
        """This is executed when searching through the box in the navigation.

        We build the query string and redirect it to this view again.

        """
        form = WlSearchForm(request.POST)
        if form.is_valid() and form.cleaned_data["q"] != "":
            # Query string
            search_url = f"q={form.cleaned_data['q']}"

            section = choices.get(request.POST["section"], "all")
            if section == "all":
                # Add initial values of all the form fields
                for field, v in form.fields.items():
                    if field == "q":
                        # Don't change the query string
                        continue
                    search_url += f"&{field}={v.initial}"
            else:
                # A particular section was chosen
                search_url += f"&{section}=True"
                # Set initial start date
                search_url += f"&start_date={form.fields['start_date'].initial}"

            return HttpResponseRedirect(f"{reverse('search')}?{search_url}")

        # Form invalid or no search query was given
        form = WlSearchForm()
        return render(request, "search/search.html", {"form": form})

    else:  # request.GET or other requests
        form = WlSearchForm(request.GET)
        if form.is_valid() and form.cleaned_data["q"] != "":
            context = {"form": form, "query": form.cleaned_data["q"], "result": {}}
            # Search the models depending on the given sections and add one
            # page of results of each model, if any is found, to the context
            page = request.GET.get("page", 1)
            for section, result_lists in sections.items():
                if not form.cleaned_data[section]:
                    continue
                for name, model in result_lists.items():
                    results = _results_page(form.search(model), page)
                    if results:
                        context["result"][name] = results

            return render(request, "search/search.html", context)

        # Form errors or no search query was given
        return render(request, "search/search.html", {"form": form})
