from django.core.management.base import BaseCommand, CommandError
from wlimages.models import Image
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Find wlimage objects without a file and files without a wlimage object"

    def handle(self, *args, **options):
        image_files = []

        for f in os.listdir(os.path.join(settings.MEDIA_ROOT, "wlimages")):
            image_files.append(
                os.path.join(settings.MEDIA_ROOT, "wlimages", f))

        # Files without a wlimage object
        files_wo_wlimage = image_files.copy()
        # wlimage objects without a file
        wlimage_wo_file = []

        for img in Image.objects.all():
            try:
                # throws FileNotFoundError
                img.image.file
                # no error
                if img.image.path in image_files:
                    files_wo_wlimage.pop(
                        files_wo_wlimage.index(img.image.path))
            except FileNotFoundError as e:
                wlimage_wo_file.append(img.name)
            except IndexError as e:
                error = "{}\nProbably the code is faulty".format(e)
                raise CommandError(error)
            except Exception as e:
                error = "ERROR: {}\nFor object: {}".format(e, img)
                raise CommandError(error)


        self.stdout.write(self.style.ERROR("Theses files have no wlimage object:"))
        for x in files_wo_wlimage:
            self.stdout.write(x)
        self.stdout.write(self.style.ERROR("These wlimage objects have no file:"))
        for x in wlimage_wo_file:
            self.stdout.write(x)
