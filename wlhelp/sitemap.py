from django.contrib.sitemaps import Sitemap
from wlhelp.models import Tribe, Building, Ware, Worker


class WlHelpTribeSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Tribe.objects.all()

    def location(self, obj):
        return '/encyclopedia/%s' % obj.name


class WlHelpBuildingSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Building.objects.all()

    def location(self, obj):
        return '/encyclopedia/%s/buildings/%s' % (obj.tribe.name, obj.name)


class WlHelpWareSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Ware.objects.all()

    def location(self, obj):
        return '/encyclopedia/%s/wares/%s' % (obj.tribe.name, obj.name)


class WlHelpWorkerSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.5

    def items(self):
        return Worker.objects.all()

    def location(self, obj):
        return '/encyclopedia/%s/workers/%s' % (obj.tribe.name, obj.name)
