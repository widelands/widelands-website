from collections.abc import Callable
from typing import NamedTuple

from django.core.paginator import InvalidPage, Paginator
from django.db.models import QuerySet
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import WlSearchForm
from .fulltext import SearchQuery, fulltext_search, substring_search
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


class ResultList(NamedTuple):
    objects: Callable[[], QuerySet]  # All searchable objects
    search: Callable  # fulltext_search() or substring_search()
    fields: list[str]  # For fulltext_search() exactly the FULLTEXT index
    order_by: tuple[str, ...]
    date_field: str | None = None  # Filtered by the start date, if any

    def results(self, query, start_date):
        objects = self.objects()
        if self.date_field and start_date:
            objects = objects.filter(**{f"{self.date_field}__gte": start_date})
        return self.search(objects, self.fields, query).order_by(*self.order_by)


def _forum_topics():
    """Topics without hidden posts outside of internal forums."""
    return (
        Topic.objects.filter(forum__category__internal=False)
        .exclude(posts__hidden=True)
        .select_related("forum", "user")
    )


def _forum_posts():
    """Visible posts of visible topics outside of internal forums."""
    return (
        ForumPost.objects.filter(topic__forum__category__internal=False)
        .exclude(hidden=True)
        .exclude(topic__in=Topic.objects.hidden())
        .select_related("topic__forum", "user")
    )


def _encyclopedia(model):
    # The encyclopedia is small and its search also matches the tribe name,
    # so it has no FULLTEXT index.
    return ResultList(
        lambda: model.objects.select_related("tribe"),
        substring_search,
        ["help", "displayname", "tribe__name"],
        ("tribe__name", "displayname"),
    )


# The result lists shown for each section checkbox of the search form. The
# FULLTEXT indexes are created by the wlsearch migrations.
sections = {
    "incl_forum": {
        "topics": ResultList(
            _forum_topics, fulltext_search, ["name"], ("-created",), "created"
        ),
        "posts": ResultList(
            _forum_posts, fulltext_search, ["body_text"], ("-created",), "created"
        ),
    },
    "incl_wiki": {
        "wiki": ResultList(
            lambda: Article.objects.filter(deleted=False),
            fulltext_search,
            ["title", "content", "summary"],
            ("title",),
        ),
    },
    "incl_news": {
        "news": ResultList(
            NewsPost.objects.published,
            fulltext_search,
            ["title", "body"],
            ("-publish",),
            "publish",
        ),
    },
    "incl_maps": {
        "maps": ResultList(
            Map.objects.all,
            fulltext_search,
            ["name", "author", "descr", "uploader_comment"],
            ("name",),
        ),
    },
    "incl_help": {
        "workers": _encyclopedia(Worker),
        "wares": _encyclopedia(Ware),
        "buildings": _encyclopedia(Building),
    },
}


def _results_page(results, number):
    """Return the requested page of search results, or None if it does not
    exist."""
    try:
        return Paginator(results, RESULTS_PER_PAGE).page(number)
    except InvalidPage:
        return None


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
            query = SearchQuery(form.cleaned_data["q"])
            start_date = form.cleaned_data["start_date"]
            page = request.GET.get("page", 1)
            for section, result_lists in sections.items():
                if not form.cleaned_data[section]:
                    continue
                for name, result_list in result_lists.items():
                    results = _results_page(
                        result_list.results(query, start_date), page
                    )
                    if results:
                        context["result"][name] = results

            return render(request, "search/search.html", context)

        # Form errors or no search query was given
        return render(request, "search/search.html", {"form": form})
