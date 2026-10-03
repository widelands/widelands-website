from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from . import app_settings, get_star_ratings_rating_model
from .models import UserRating


class UserRatingAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("rating", "user")
            .prefetch_related("rating__content_object")
        )

    @admin.display(description=_("Score"))
    def stars(self, obj):
        html = (
            "<span style='display: block; width: {}px; height: 10px; "
            "background: url(/static/star-ratings/images/admin_stars.png)'>&nbsp;</span>"
        )
        return format_html(html, obj.score * 10)

    list_display = ("__str__", "stars")


class RatingAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("content_object")

    @admin.display(description=_("Rating average"))
    def stars(self, obj):
        html = (
            "<div style='position: relative;'>"
            "<span style='position: absolute; top: 0; left: 0; width: {}px; height: 10px; "
            "background: url(/static/star-ratings/images/admin_stars.png) 0px 10px'>&nbsp;</span>"
            "<span style='position: absolute; top: 0; left: 0; width: {}px; height: 10px; "
            "background: url(/static/star-ratings/images/admin_stars.png)'>&nbsp;</span>"
            "</div>"
        )
        return format_html(html, app_settings.STAR_RATINGS_RANGE * 10, obj.average * 10)

    list_display = ("__str__", "stars")


admin.site.register(get_star_ratings_rating_model(), RatingAdmin)
admin.site.register(UserRating, UserRatingAdmin)
