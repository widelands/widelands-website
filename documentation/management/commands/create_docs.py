#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create the source code documenation.

This script covers all needed steps to create or recreate the widelands
source code documentation.

Needed dependency: Sphinx

"""

from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
import sys
import imp
import shutil
import glob
from subprocess import check_call, CalledProcessError

class Command(BaseCommand):
    help = 'Create the source code documenation.'
        
    def move_docs(self, build_dir):
        """Move the documentation created by sphinxdoc to the correct folder.
    
        On unix systems the files were served from the symlink called
        'html'. On Windows systems the files will only be copied in a folder
        called 'html'.
    
        """
    
        if os.name == 'posix':
            try:
                # Creating symlinks is only available on unix systems
                link_name = os.path.join(
                    settings.MEDIA_ROOT, 'documentation/html')
                target_dir = os.path.join(
                    settings.MEDIA_ROOT, 'documentation/current')
    
                if not os.path.exists(target_dir):
                    # only needed on first run
                    os.mkdir(target_dir)
    
                if os.path.exists(link_name):
                    # only needed if this script has already run
                    os.remove(link_name)
    
                # Temporarily switch the symlink
                os.symlink(build_dir, link_name)
                # Remove current
                shutil.rmtree(target_dir)
                # Copy new build to current
                shutil.copytree(build_dir, target_dir)
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
                shutil.copytree(build_dir, target_dir)
            except:
                raise
    
        # The newly created directory is no longer needed
        shutil.rmtree(build_dir)
    
    
    def handle(self, *args, **options):
        """Create the widelands source code documentation.
    
        The Documenatation is build by sphinxdoc in the directory
        'settings/MEDIA/documentation/html_temp'.
    
        """
    
        sphinx_dir = os.path.join(settings.WIDELANDS_SVN_DIR, 'doc/sphinx')
        build_dir = os.path.join(settings.MEDIA_ROOT, 'documentation/html_temp')
    
        if not os.path.exists(sphinx_dir):
            print("Can't find the directory given by WIDELANDS_SVN_DIR in local_settings.py:\n", sphinx_dir)
            sys.exit(1)
    
        if os.path.exists(os.path.join(sphinx_dir, 'build')):
    
            # Clean the autogen* files created by extract_rst.py
            # This has to be done because sometimes such a file remains after
            # removing it from extract_rst. sphinx-build throughs an error then.
            try:
                for f in glob.glob(os.path.join(sphinx_dir, 'source/autogen*')):
                    os.remove(f)
            except OSError:
                raise
    
        # Locally 'dirhtml' do not work because the staticfiles view disallow
        # directory indexes, but 'dirhtml' gives nicer addresses in production
        builder = 'html'
        if not settings.DEBUG:
            # In production DEBUG is False
            builder = 'dirhtml'
    
        try:
            check_call(['python', os.path.join(sphinx_dir, 'extract_rst.py')])
            check_call(['sphinx-build',
                        '-b', builder,
                        '-d', os.path.join(sphinx_dir, 'build/doctrees'),
                        '-c', os.path.join(build_dir, '../../../documentation'),
                        os.path.join(sphinx_dir, 'source'),
                        os.path.join(build_dir),
                        ])
        except CalledProcessError as why:
            print('An error occured: {0}'.format(why))
            sys.exit(1)
    
        self.move_docs(build_dir)
