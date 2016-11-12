from news.models import Post
from django.views.generic import ArchiveIndexView, YearArchiveView, MonthArchiveView
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
