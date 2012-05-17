from ...models import Tribe as TribeModel

from django.core.management.base import BaseCommand, CommandError
from settings import MEDIA_ROOT, WIDELANDS_SVN_DIR, MEDIA_URL

import os
import shutil
from os import path
from widelandslib.tribe import *
from widelandslib.make_flow_diagram import make_graph

class Command(BaseCommand):
    help =\
    """Update the overview pdfs of all tribes in a current checkout"""

    def handle(self, directory = WIDELANDS_SVN_DIR, **kwargs):
        tribes = [d for d in glob("%s/tribes/*" % directory)
                    if os.path.isdir(d)]

        print "updating pdf files for all tribes"

        for t in tribes:
            tribename = os.path.basename(t)
            print "  updating pdf file for tribe ", tribename
            gdir = make_graph(tribename)
            pdffile = path.join(gdir, tribename + ".pdf")
            giffile = path.join(gdir, tribename + ".gif")

            targetdir = path.join(MEDIA_ROOT, "wlhelp", "network_graphs", tribename)

            try:
                os.makedirs(targetdir)
            except OSError:
                pass

            shutil.copy(pdffile, targetdir)
            shutil.copy(giffile, targetdir)

            shutil.rmtree(gdir)
