#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create the source code documenation.

This script covers all needed steps to create or recreate the widelands
source code documentation.

Needed dependency: Sphinx

"""


from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from subprocess import check_call, CalledProcessError
from documentation import conf
import os
import sys
import shutil
import glob


class Command(BaseCommand):
    help = 'Create the source code documenation.'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # Define the main directories used in this class
        self.sphinx_dir = os.path.join(
            settings.WIDELANDS_SVN_DIR, 'doc/sphinx')
        self.build_dir = os.path.join(
            settings.MEDIA_ROOT, 'documentation/html_temp')
        self.sphinx_conf_dir = os.path.dirname(conf.__file__)

    def move_docs(self):
        """Move the documentation created by sphinxdoc to the correct folder.

        On unix systems the files were served from the symlink called
        'html'. On Windows systems the files will only be copied in a
        folder called 'html'.

        """

        if os.name == 'posix':
            # Creating symlinks is only available on unix systems
            try:
                link_name = os.path.join(
                    settings.MEDIA_ROOT, 'documentation/html')
                target_dir = os.path.join(
                    settings.MEDIA_ROOT, 'documentation/current')

                if not os.path.exists(target_dir):
                    # only needed on first run
                    os.mkdir(target_dir)

                if os.path.lexists(link_name):
                    # only needed if this script has already run
                    os.remove(link_name)

                # Temporarily switch the symlink
                os.symlink(self.build_dir, link_name)
                # Remove current
                shutil.rmtree(target_dir)
                # Copy new build to current
                shutil.copytree(self.build_dir, target_dir)
                # Switch the link to current
                os.remove(link_name)
                os.symlink(target_dir, link_name)
            except:
                raise
        else:
            # Non unix OS: Copy docs
            try:
                target_dir = os.path.join(
                    settings.MEDIA_ROOT, 'documentation/html')
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                shutil.copytree(self.build_dir, target_dir)
            except:
                raise

        try:
            # The new build directory is no longer needed
            shutil.rmtree(self.build_dir)
        except:
            raise

    def handle(self, *args, **options):
        """Create the widelands source code documentation.

        The Documenatation is built by sphinxdoc in the directory
        'settings/MEDIA/documentation/html_temp'.

        """

        if not os.path.exists(self.sphinx_dir):
            print(
                "Can't find the directory given by WIDELANDS_SVN_DIR in local_settings.py:\n", self.sphinx_dir)
            sys.exit(1)

        if os.path.exists(os.path.join(self.sphinx_dir, 'build')):
            # Clean the autogen* files created by extract_rst.py
            # This has to be done because sometimes such a file remains after
            # removing it from extract_rst.
            try:
                for f in glob.glob(os.path.join(self.sphinx_dir, 'source/autogen*')):
                    os.remove(f)
            except OSError:
                raise

        builder = 'dirhtml'

        try:
            check_call(['python', os.path.join(
                self.sphinx_dir, 'extract_rst.py'), '-graphs'])
            check_call(['sphinx-build',
                        '-b', builder,
                        '-d', os.path.join(self.sphinx_dir, 'build/doctrees'),
                        '-c', self.sphinx_conf_dir,
                        os.path.join(self.sphinx_dir, 'source'),
                        self.build_dir,
                        ])
        except CalledProcessError as why:
            print('An error occured: {0}'.format(why))
            sys.exit(1)

        self.move_docs()
