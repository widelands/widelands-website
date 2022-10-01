from ...models import Tribe as TribeModel

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import os
import shutil
from os import path
from widelandslib.tribe import *
from widelandslib.make_flow_diagram import make_graph
from wlhelp.models import Tribe
from glob import glob
import json


class Command(BaseCommand):
    help = """Update the overview pdfs of all tribes in a current checkout"""

    def handle(
        self,
        json_directory=os.path.normpath(settings.MEDIA_ROOT + "/map_object_info"),
        **kwargs
    ):
        with open(
            os.path.normpath(json_directory + "/tribes.json"), "r"
        ) as source_file:
            tribesinfo = json.load(source_file)

        print("updating pdf files for all tribes")

        for t in tribesinfo["tribes"]:
            tribename = t["name"]
            print("  updating pdf file for tribe ", tribename)
            gdir = make_graph(tribename)
            pdffile = path.join(gdir, tribename + ".pdf")
            giffile = path.join(gdir, tribename + ".gif")

            targetdir = path.normpath(
                path.join(settings.MEDIA_ROOT, "wlhelp", "network_graphs", tribename)
            )

            try:
                os.makedirs(targetdir)
            except OSError:
                pass

            shutil.copy(pdffile, targetdir)
            shutil.copy(giffile, targetdir)

            tribe = Tribe.objects.get(name=tribename)
            if tribe:
                tribe.network_pdf_url = path.normpath(
                    "%s/%s/%s"
                    % (
                        settings.MEDIA_URL,
                        targetdir[len(settings.MEDIA_ROOT) :],
                        tribename + ".pdf",
                    )
                )
                tribe.network_gif_url = path.normpath(
                    "%s/%s/%s"
                    % (
                        settings.MEDIA_URL,
                        targetdir[len(settings.MEDIA_ROOT) :],
                        tribename + ".gif",
                    )
                )
                tribe.save()
            else:
                print("Could not set tribe urls")

            shutil.rmtree(gdir)
