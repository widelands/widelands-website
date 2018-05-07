#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create the source code documenation.

This script covers all needed steps to create or recreate the widelands
source code documentation.

Needed dependency: Sphinx

"""

from __future__ import print_function
import os
import sys
import imp
import shutil
import glob
from subprocess import check_call, CalledProcessError


def get_local_settings():
    """Get local_settings."""

    # Didn't find a better way to get the settings from the parent directory
    try:
        f, f_path, descr = imp.find_module('../local_settings')
        settings = imp.load_module('local_settings', f, f_path, descr)
    except ImportError as why:
        print("Couldn't find local_settings.py! ", why)
        sys.exit(1)
    else:
        f.close()

    global SPHINX_DIR, BUILD_DIR
    SPHINX_DIR = os.path.join(settings.WIDELANDS_SVN_DIR, 'doc/sphinx')
    BUILD_DIR = os.path.join(settings.MEDIA_ROOT, 'documentation/html_temp')

    return settings


def move_docs(settings):
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
            os.symlink(BUILD_DIR, link_name)
            # Remove current
            shutil.rmtree(target_dir)
            # Copy new build to current
            shutil.copytree(BUILD_DIR, target_dir)
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
            shutil.copytree(BUILD_DIR, target_dir)
        except:
            raise

    # The newly created directory is no longer needed
    shutil.rmtree(BUILD_DIR)


def create_sphinxdoc():
    """Create the widelands source code documentation.

    The Documenatation is build by sphinxdoc directly in the directory
    'settings/MEDIA/documentation/html_temp'.

    """

    settings = get_local_settings()

    if not os.path.exists(SPHINX_DIR):
        print("Can't find the directory given by WIDELANDS_SVN_DIR in local_settings.py:\n", SPHINX_DIR)
        sys.exit(1)

    # Locally 'dirhtml' do not work because the staticfiles view disallow
    # directory indexes, but 'dirhtml' gives nicer addresses in production
    builder = 'html'
    if hasattr(settings, 'DEBUG'):
        # In production local_settings.py has no DEBUG statement
        builder = 'dirhtml'

    try:
        check_call(['python', os.path.join(SPHINX_DIR, 'extract_rst.py')])
        check_call(['sphinx-build',
                    '-b', builder,
                    '-d', os.path.join(SPHINX_DIR, 'build/doctrees'),
                    os.path.join(SPHINX_DIR, 'source'),
                    os.path.join(BUILD_DIR),
                    ])
    except CalledProcessError as why:
        print('An error occured: {0}'.format(why))
        sys.exit(1)

    move_docs(settings)

if __name__ == '__main__':
    try:
        from django.conf import settings
    except ImportError:
        print('Are you running this script with activated virtual environment?')
        sys.exit(1)

    sys.exit(create_sphinxdoc())
