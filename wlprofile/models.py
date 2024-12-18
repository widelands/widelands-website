from django.db import models
from django.contrib.auth.models import User
from .fields import ExtendedImageField
from mainpage.wl_utils import AutoOneToOneField
from django.utils.translation import gettext_lazy as _
from pybb.models import Post
from wlhelp.models import Tribe

from django.conf import settings

TZ_CHOICES = [
    (float(x[0]), x[1])
    for x in (
        (-12, "UTC -12"),
        (-11, "UTC -11"),
        (-10, "UTC -10"),
        (-9.5, "UTC -09.5"),
        (-9, "UTC -09"),
        (-8.5, "UTC -08.5"),
        (-8, "UTC -08"),
        (-7, "UTC -07"),
        (-6, "UTC -06"),
        (-5, "UTC -05"),
        (-4, "UTC -04"),
        (-3.5, "UTC -03.5"),
        (-3, "UTC -03"),
        (-2, "UTC -02"),
        (-1, "UTC -01"),
        (0, "UTC"),
        (1, "UTC +01"),
        (2, "UTC +02"),
        (3, "UTC +03"),
        (3.5, "UTC +03.5"),
        (4, "UTC +04"),
        (4.5, "UTC +04.5"),
        (5, "UTC +05"),
        (5.5, "UTC +05.5"),
        (5.75, "UTC +05.45"),
        (6, "UTC +06"),
        (6.5, "UTC +06.5"),
        (7, "UTC +07"),
        (8, "UTC +08"),
        (9, "UTC +09"),
        (9.5, "UTC +09.5"),
        (10, "UTC +10"),
        (10.5, "UTC +10.5"),
        (11, "UTC +11"),
        (11.5, "UTC +11.5"),
        (12, "UTC +12"),
        (12.75, "UTC +12.75"),
        (13, "UTC +13"),
        (14, "UTC +14"),
    )
]


class Profile(models.Model):
    user = AutoOneToOneField(
        User, related_name="wlprofile", verbose_name=_("User"), on_delete=models.CASCADE
    )

    operating_system = models.CharField(
        _("Operating System"),
        max_length=100,
        blank=True,
        default="",
    )

    widelands_version = models.CharField(
        _("Widelands Version"),
        max_length=255,
        blank=True,
        default="",
    )

    webservice_nick = models.CharField(
        _("Webservice/Nick"),
        max_length=255,
        blank=True,
        default="",
    )

    favourite_map = models.CharField(
        _("Your favourite Map(s)"),
        max_length=100,
        blank=True,
        default="",
    )

    favourite_tribe = models.ForeignKey(
        Tribe,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    favourite_addon = models.CharField(
        _("Your favourite Add-On"),
        max_length=255,
        blank=True,
        default="",
    )

    # Personal Informations
    location = models.CharField(_("Location"), max_length=30, blank=True, default="")

    # Configuration for Forum/Site
    time_zone = models.FloatField(_("Time zone"), choices=TZ_CHOICES, default=0.0)
    time_display = models.CharField(
        _("Time display"), max_length=80, default=settings.DEFAULT_TIME_DISPLAY
    )
    signature = models.TextField(
        _("Signature"), blank=True, default="", max_length=settings.SIGNATURE_MAX_LENGTH
    )

    avatar = ExtendedImageField(
        _("Avatar"),
        blank=True,
        default="wlprofile/anonymous.png",
        upload_to="wlprofile/avatars/",
        width=settings.AVATAR_WIDTH,
        height=settings.AVATAR_HEIGHT,
    )
    show_signatures = models.BooleanField(
        _("Show signatures"), blank=True, default=True
    )
    deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def post_count(self):
        """Return the nr of posts the user has.

        This uses djangos filter feature will therefore hit the
        database. This should maybe be reworked when the database grows
        to not be always calculated.

        """
        return Post.objects.public().filter(user=self.user).count()

    def user_status(self):
        nump = self.post_count()

        if nump < 6:
            return {"text": "Just found this site", "image": "rang_1.png"}
        elif nump < 50:
            return {"text": "Pry about Widelands", "image": "rang_2.png"}
        elif nump < 120:
            return {"text": "Likes to be here", "image": "rang_3.png"}
        elif nump < 180:
            return {"text": "At home in WL-forums", "image": "rang_4.png"}
        elif nump < 250:
            return {"text": "Widelands-Forum-Junkie", "image": "rang_5.png"}
        elif nump < 500:
            return {"text": "Tribe Member", "image": "rang_6.png"}
        else:
            return {"text": "One Elder of Players", "image": "rang_7.png"}
