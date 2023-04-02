from django.db import models
from django.contrib.auth.models import User


class AddonNoticeType(models.Model):
    display = models.CharField(max_length=50, help_text="E.g.: Translation issues")
    description = models.CharField(
        max_length=100, help_text="E.g.: Notify me on translation issues"
    )
    send_default = models.BooleanField(
        default=True, help_text="Default setting for this notice type"
    )
    author_related_default = models.BooleanField(
        default=True,
        help_text="Turn off for notice types which are not directly related\
                   to an add-on author, e.g. mentions in add-on comments.",
    )
    slug = models.SlugField(unique=True, help_text="Do not change this once it is set")

    def __str__(self):
        return self.display

    class Meta:
        verbose_name = "Addon notice type"
        verbose_name_plural = "Addon notice types"


class AddonNoticeUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notice_type = models.ForeignKey(AddonNoticeType, on_delete=models.CASCADE)
    shouldsend = models.BooleanField(default=True)
    author_related = models.BooleanField(default=True)

    def __str__(self):
        return self.notice_type.display

    class Meta:
        verbose_name = "Addon noticetype/user relationship"
        verbose_name_plural = "Addon noticetype/user relationships"


def get_addons_for_user(user_pk):
    """Fetch the addon-names for this user from the add-ons database."""

    from django.db import connections

    user_addons = []

    # not try-clause to get admins informed on a failure
    cursor = connections["addonserver"].cursor()
    cursor.execute(
        "SELECT addons.name\
        FROM uploaders, addons\
        WHERE uploaders.addon=addons.id\
        AND uploaders.user=%s",
        [user_pk],
    )

    user_addons = cursor.fetchall()
    cursor.close()
    return user_addons


def get_addon_usersetting(user, noticetype):
    """Returns the usersetting for a user and the names of Add-Ons this user
    has created."""

    usersetting = None

    usersetting, created = AddonNoticeUser.objects.update_or_create(
        user=user,
        notice_type=noticetype,
    )
    if created:
        usersetting.shouldsend = noticetype.send_default
        usersetting.author_related = noticetype.author_related_default
        usersetting.save()

    return usersetting
