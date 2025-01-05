from django.core.management.base import BaseCommand
from check_input.models import SuspiciousInput
from django.core.mail import mail_admins
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Send email if suspicious content is found"

    def handle(self, *args, **options):
        spams = SuspiciousInput.objects.all()
        if spams:
            message = "There were %d hidden posts found:" % len(spams)

            for spam in spams:
                app = ContentType.objects.get_for_id(spam.content_type_id)
                message += "\nIn %s/%s: " % (app.app_label, app.model)
                message += "\n User '%s' wrote: %s" % (spam.user, spam.text)

            message += (
                "\n\nAdmin page: https://%s/admin/pybb/post/"
                % Site.objects.get_current().domain
            )
            mail_admins(
                "Hidden posts were found",
                message,
                fail_silently=False,
            )
