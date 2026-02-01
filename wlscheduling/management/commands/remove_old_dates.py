from django.core.management.base import BaseCommand
from wlscheduling.models import Availabilities
from datetime import datetime


class Command(BaseCommand):
    help = "Removes dates that are already passed"

    def handle(self, *args, **options):
        for date in Availabilities.objects.all():
            if datetime.utcnow() > date.avail_time:
                date.delete()
