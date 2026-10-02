from wlhelp.models import Tribe, Building, Ware, Worker
from mainpage.sitemaps import SitemapHTTPS


class WlHelpTribeSitemap(SitemapHTTPS):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        return Tribe.objects.all()

    def location(self, obj):
        return f"/encyclopedia/{obj.name}"


class WlHelpBuildingSitemap(SitemapHTTPS):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        return Building.objects.all()

    def location(self, obj):
        return f"/encyclopedia/{obj.tribe.name}/buildings/{obj.name}"


class WlHelpWareSitemap(SitemapHTTPS):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        return Ware.objects.all()

    def location(self, obj):
        return f"/encyclopedia/{obj.tribe.name}/wares/{obj.name}"


class WlHelpWorkerSitemap(SitemapHTTPS):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        return Worker.objects.all()

    def location(self, obj):
        return f"/encyclopedia/{obj.tribe.name}/workers/{obj.name}"
