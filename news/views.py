from django.shortcuts import get_object_or_404
from news.models import Post, Category
from django.views.generic import (
    ListView,
    ArchiveIndexView,
    YearArchiveView,
    MonthArchiveView,
    DateDetailView,
)


class NewsList(ArchiveIndexView):

    template_name = "news/category_posts.html"
    model = Post
    date_field = "publish"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(NewsList, self).get_context_data(**kwargs)
        page_obj = context['page_obj']
        context.update(
            {
                "paginator_range": page_obj.paginator.get_elided_page_range(
                    page_obj.number, on_each_side=2),
            }
        )

        context["categories"] = page_obj
        return context


class YearNews(YearArchiveView):

    model = Post
    template_name = "news/post_archive_year.html"
    date_field = "publish"
    make_object_list = True
    paginate_by = 20

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(YearNews, self).get_context_data(**kwargs)
        page_obj = context['page_obj']
        context.update(
            {
                "paginator_range": page_obj.paginator.get_elided_page_range(
                    page_obj.number, on_each_side=2),
            }
        )

        context["categories"] = page_obj
        return context


class MonthNews(MonthArchiveView):

    model = Post
    template_name = "news/post_archive_month.html"
    date_field = "publish"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MonthArchiveView, self).get_context_data(**kwargs)
        page_obj = context['page_obj']
        context.update(
            {
                "paginator_range": page_obj.paginator.get_elided_page_range(
                    page_obj.number, on_each_side=2),
            }
        )

        context["categories"] = page_obj
        return context


class NewsDetail(DateDetailView):

    model = Post
    template_name = "news/post_detail.html"
    date_field = "publish"


class CategoryView(ListView):

    template_name = "news/category_posts.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CategoryView, self).get_context_data(**kwargs)
        if self.kwargs["slug"] == "none":
            # Exemption for posts with no category
            context["cur_category"] = "None"
        else:
            context["cur_category"] = get_object_or_404(
                Category, slug=self.kwargs["slug"]
            )
        page_obj = context['page_obj']
        context.update(
            {
                "paginator_range": page_obj.paginator.get_elided_page_range(
                    page_obj.number, on_each_side=2),
            }
        )

        context["categories"] = Category.objects.all()
        return context

    def get_queryset(self):
        # Gather posts filtered by category
        if self.kwargs["slug"] == "none":
            # Posts mustn't have a category
            qs = Post.objects.published().filter(categories=None)
        else:
            qs = Post.objects.published().filter(categories__slug=self.kwargs["slug"])
        return qs
