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
            # Search the models depending on the given section
            # Add search results, if any is found, to the context
            if form.cleaned_data["incl_forum"]:
                topic_results = [x for x in form.search(Topic)]
                post_results = [x for x in form.search(ForumPost)]
                if len(topic_results):
                    context["result"].update({"topics": topic_results})
                if len(post_results):
                    context["result"].update({"posts": post_results})

            if form.cleaned_data["incl_wiki"]:
                wiki_results = [x for x in form.search(Article)]
                if len(wiki_results):
                    context["result"].update({"wiki": wiki_results})

            if form.cleaned_data["incl_news"]:
                news_results = [x for x in form.search(NewsPost)]
                if len(news_results):
                    context["result"].update({"news": news_results})

            if form.cleaned_data["incl_maps"]:
                map_results = [x for x in form.search(Map)]
                if len(map_results):
                    context["result"].update({"maps": map_results})

            if form.cleaned_data["incl_help"]:
                worker_results = [x for x in form.search(Worker)]
                ware_results = [x for x in form.search(Ware)]
                building_results = [x for x in form.search(Building)]
                if len(worker_results):
                    context["result"].update({"workers": worker_results})
                if len(ware_results):
                    context["result"].update({"wares": ware_results})
                if len(building_results):
                    context["result"].update({"buildings": building_results})

            return render(request, "search/search.html", context)

        # Form errors or no search query was given
        return render(request, "search/search.html", {"form": form})
