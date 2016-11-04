from django.contrib.sitemaps import Sitemap
from django.contrib import sitemaps
from datetime import datetime
from datetime import timedelta
from pybb.models import Forum
from wlhelp.models import Tribe
from django.core.urlresolvers import reverse


class ForumSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Forum.objects.all()

class WlHelpSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['encyclopedia']#Tribe.objects.all()
    
    def location(self, item):
        print('franku object', reverse(item))
        return reverse(item)