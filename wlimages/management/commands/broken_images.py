from django.core.management.base import BaseCommand, CommandError
from wlimages.models import Image
from django.conf import settings
from wiki.models import Article
import os


class Command(BaseCommand):
    help = "Find wlimage objects without a file and files without a wlimage object"

    def handle(self, *args, **options):

        def _is_used(f_path):
            # Try to find an article where this image is shown
            for article in Article.objects.all():
                f_name = f_path.rsplit("/", 1)[1]
                if f_name in article.content:
                    return article
            return None

        image_files = []

        for f in os.listdir(os.path.join(settings.MEDIA_ROOT, "wlimages")):
            image_files.append(os.path.join(settings.MEDIA_ROOT, "wlimages", f))

        # Files without a wlimage object
        files_wo_wlimage = image_files.copy()
        # wlimage objects without a file
        wlimage_wo_file = []

        for img in Image.objects.all():
            try:
                # throws FileNotFoundError if the underlying file is not found
                img.image.file
                # no error
                if img.image.path in image_files:
                    files_wo_wlimage.pop(files_wo_wlimage.index(img.image.path))
            except FileNotFoundError:
                wlimage_wo_file.append(img.name)
            except IndexError as e:
                error = "{}\nProbably the code is faulty?".format(e)
                raise CommandError(error)
            except Exception as e:
                error = "ERROR: {}\nFor object: {}".format(e, img)
                raise CommandError(error)

        # An image file might have no wlimage object but is used in an article
        # Try to find an article where this file is shown
        files_wo_wlimage_used = {}
        for img_file in files_wo_wlimage:
            files_wo_wlimage_used[img_file] = _is_used(img_file)

        self.stdout.write(self.style.ERROR("Theses files have no wlimage object:"))
        for f_path, article in files_wo_wlimage_used.items():
            self.stdout.write(f_path)
            if article:
                self.stdout.write("  Linked in article: {}".format(article))

        self.stdout.write(self.style.ERROR("These wlimage objects have no file:"))
        for x in wlimage_wo_file:
            self.stdout.write(x)
