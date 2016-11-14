from django.shortcuts import get_object_or_404
from news.models import Post, Category
from django.views.generic import \
    ListView, \
    ArchiveIndexView, \
    YearArchiveView, \
    MonthArchiveView, \
    DetailView
import datetime


class NewsList(ArchiveIndexView):

    queryset = Post.objects.published()
    date_field = 'publish'


class YearNews(YearArchiveView):

    queryset = Post.objects.published()
    date_field = 'publish'
    make_object_list = True


class MonthNews(MonthArchiveView):

    queryset = Post.objects.published()
    template_name = 'post_archive_year.html'
    date_field = 'publish'


class NewsDetail(DetailView):

    queryset = Post.objects.published()
    template_name = 'news/post_detail.html'


class CategoryView(ListView):

    template_name = 'news/category_posts.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CategoryView, self).get_context_data(**kwargs)
        if self.kwargs['slug'] == 'none':
            # Exemption for post with no category
            context['cur_category'] = 'None'
        else:
            context['cur_category'] = get_object_or_404(
                Category, slug=self.kwargs['slug'])

        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        # Gather posts filtered by category
        if self.kwargs['slug'] == 'none':
            # Posts mustn't have a category
            qs = Post.objects.published().filter(categories=None)
        else:
            qs = Post.objects.published().filter(
                categories__slug=self.kwargs['slug'])
        return qs
