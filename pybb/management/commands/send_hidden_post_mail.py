from django.core.management.base import BaseCommand
from pybb.models import Post
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Send emails if hidden posts are found'

    def handle(self, *args, **options):
        hidden_posts = Post.objects.filter(hidden=True)

        if hidden_posts:
            message = 'There were %d hidden posts found:' % len(hidden_posts)
            for post in hidden_posts:
                message += '\n' + post.user.username + ': ' + post.body_text[:70]

            message += '\n\nAdmin page: ' + Site.objects.get_current().domain + \
                '/admin/pybb/post/'
            recipients = [addr[1] for addr in settings.ADMINS]
            send_mail('Hidden posts were found', message, 'pybb@widelands.org',
                      recipients, fail_silently=False)
