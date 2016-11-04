from django.contrib.sitemaps import Sitemap
from wlhelp.models import Tribe, Ware, Worker


class WlHelpSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        t = Tribe.objects.all()
        return t
    
    def location(self, obj):
        print('franku obj: ', obj)
        return '/encyclopedia/%s' % obj.name

class WlHelpTribeSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Tribe.objects.all()
    
    def location(self, obj):
        return '/%s' % obj.name

class WlHelpWareSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Ware.objects.all()
    
    def location(self, obj):
        return '/%s' % obj.name

class WlHelpWorkerSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Worker.objects.all()
    
    def location(self, obj):
        return '/%s' % obj.name