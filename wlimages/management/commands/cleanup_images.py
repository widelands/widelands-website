from django.core.management.base import BaseCommand, CommandError
from django.core.mail import mail_admins
from wlimages.models import Image
from django.conf import settings
from wiki.models import Article
import os
import datetime

IMAGE_PATH = os.path.join(settings.MEDIA_ROOT, "wlimages")
BACKUP_FOLDER = os.path.join(
    IMAGE_PATH,
    "cleanup_images_backup_{}".format(datetime.date.today().isoformat()),
)


class Command(BaseCommand):
    help = "Find wlimage objects without a file and files without a wlimage object"

    def add_arguments(self, parser):
        # Named arguments
        parser.add_argument(
            "--delete_all",
            action="store_true",
            help="Delete files w/o wlimages and wlimages w/o files",
        )

    def handle(self, *args, **options):

        def _move_to_backup(f_path):
            try:
                if not os.path.isdir(BACKUP_FOLDER):
                    os.mkdir(BACKUP_FOLDER)

                dest_path = os.path.join(BACKUP_FOLDER, os.path.basename(f_path))
                os.rename(f_path, dest_path)
            except Exception as e:
                raise CommandError(e)

        def _get_usage(f_path):
            # Try to find any articles containing this file name
            found_articles = []
            f_name = os.path.basename(f_path)

            for article in Article.objects.all():
                if f_name in article.content:
                    found_articles.append(article.__str__())

            return found_articles

        image_files = []
        for f in os.scandir(IMAGE_PATH):
            if f.is_file(follow_symlinks=False):
                # Don't include backup dir
                image_files.append(os.path.join(IMAGE_PATH, f))

        # Files without a wlimage object
        files_wo_wlimage = {}
        for img in image_files:
            files_wo_wlimage[img] = []

        # wlimage objects without a file
        wlimage_wo_file = []

        for img in Image.objects.all():
            try:
                # throws FileNotFoundError if the underlying file is not found
                img.image.file
                # no error
                if img.image.path in image_files:
                    del files_wo_wlimage[img.image.path]
            except FileNotFoundError:
                wlimage_wo_file.append(img.name)
            except KeyError as e:
                error = "{}\nProbably the code is faulty?".format(e)
                raise CommandError(error)
            except Exception as e:
                error = "ERROR: {}\nFor object: {}".format(e, img)
                raise CommandError(error)

        # An image file might have no wlimage object but is used in an article
        for img_file in files_wo_wlimage.keys():
            used_in = _get_usage(img_file)
            files_wo_wlimage[img_file] = used_in

        # Finally print the results or delete related objects
        errors = []
        if files_wo_wlimage:
            if not options["delete_all"]:
                self.stdout.write(
                    self.style.ERROR("These files have no wlimage object:")
                )
            for f_path, articles in files_wo_wlimage.items():
                if options["delete_all"]:
                    if not articles:
                        # move the file only if it is NOT used in an wikiarticle
                        try:
                            _move_to_backup(f_path)
                        except FileNotFoundError as e:
                            errors.append(e)
                else:
                    self.stdout.write(f_path)
                    if articles:
                        self.stdout.write(
                            "  Used in article: {}".format(", ".join(articles))
                        )

        if wlimage_wo_file:
            if not options["delete_all"]:
                self.stdout.write(
                    self.style.ERROR("These wlimage objects have no file:")
                )
            for wlimg_name in wlimage_wo_file:
                if options["delete_all"]:
                    obj = Image.objects.get(name=wlimg_name)
                    try:
                        obj.delete()
                    except Exception as e:
                        errors.append(e)
                else:
                    self.stdout.write(wlimg_name)

        if errors:
            message = ""
            for e in errors:
                message = "{}\n\n{}".format(message, e)

            mail_admins(
                "A failure happened during executing the django management command cleanup_images",
                message,
            )
