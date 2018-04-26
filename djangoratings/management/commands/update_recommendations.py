from django.core.management.base import BaseCommand, CommandError

from djangoratings.models import SimilarUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        SimilarUser.objects.update_recommendations()
