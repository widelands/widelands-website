from news.models import Post
from django.views.generic import ListView, \
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
    date_field='publish'

class NewsDetail(DetailView):
    
    queryset=Post.objects.published()
    template_name='news/post_detail.html'

class CategoryView(ListView):
    
    template_name = 'news/category_detail.html'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['category'] = self.kwargs['slug']
        return context
    
    def get_queryset(self):
        return Post.objects.published().filter(categories__title=self.kwargs['slug'])