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
            message = f"There were {len(spams)} hidden posts found:"

            for spam in spams:
                app = ContentType.objects.get_for_id(spam.content_type_id)
                message += f"\nIn {app.app_label}/{app.model}: "
                message += f"\n User '{spam.user}' wrote: {spam.text}"

            message += (
                f"\n\nAdmin page: https://{Site.objects.get_current().domain}/admin/check_input/suspiciousinput/"
            )
            mail_admins(
                "Hidden posts were found",
                message,
                fail_silently=False,
            )
