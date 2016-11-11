from news.models import Post
from django.views.generic import ListView, YearArchiveView, MonthArchiveView
import datetime


class NewsList(ListView):
    
    template_name = 'news/post_list.html'
    
    def get_queryset(self):
        return Post.objects.exclude(status=1) #1 means 'Draft'

class YearNews(YearArchiveView):
    
    date_field="publish"
    #model = Post
    #make_object_list = True
    allow_future = True
    
    def get_queryset(self):
        since = datetime.date(int(self.get_year()), 1, 1)
        until = datetime.date(int(self.get_year()), 12, 31)
        qs = Post.objects.exclude(status=1).exclude(publish__lt=since).exclude(publish__gt=until) #1 means 'Draft'
        print('franku qs: ', qs)
        return qs

class MonthNews(MonthArchiveView):
    
    template_name = 'post_archive_year.html'
    
    def get_queryset(self):
        return Post.objects.exclude(status=1) #1 means 'Draft'