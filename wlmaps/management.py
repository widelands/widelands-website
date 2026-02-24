from django.utils.translation import gettext_noop as _

try:
    from notification import models as notification

    def create_notice_types(sender, **kwargs):
        print("Creating notice types for maps ...")
        notification.create_notice_type(
            "maps_new_map",
            _("A new Map is available"),
            _("a new map is available for download"),
            send_default=False,
        )

except ImportError:
    print("Skipping creation of NoticeTypes as notification app not found")
