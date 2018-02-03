#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create the source code documenation.

This script covers all needed steps to create or recreate the documentation.
A recreating is done if the documentation was already build (the directory
'build' exists)

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
    """Get our local_settings from django.

    Because we are running this script from outside the Django
    environment, local_settings couldn't be imported as usual.

    """

    # Didn't find a better way to get the settings from the parent directory
    try:
        f, f_path, descr = imp.find_module('../local_settings')
        return imp.load_module('local_settings', f, f_path, descr)
    except ImportError as why:
        print("Couln't find local_settings.py! ", why)
        sys.exit(1)
    else:
        f.close()


def create_docs():
    """Create the widelands source code documentation.

    Or renew the documenation as html.

    """

    settings = get_local_settings()
    SPHINX_DIR = os.path.join(settings.WIDELANDS_SVN_DIR, 'doc/sphinx')
    BUILD_DIR = os.path.join(SPHINX_DIR, 'build')

    if not os.path.exists(SPHINX_DIR):
        print("Can't find the directory given by WIDELANDS_SVN_DIR in local_settings.py:\n", SPHINX_DIR)
        sys.exit(1)

    if os.path.exists(BUILD_DIR):
        # Clean build directory
        shutil.rmtree(BUILD_DIR)

        # Clean also the autogen* files created by extract_rst.py
        # This has to be done because sometimes such a file remains after
        # removing it from extract_rst. sphinx-build throughs an error then.
        try:
            for f in glob.glob(os.path.join(SPHINX_DIR, 'source/autogen*')):
                os.remove(f)
        except OSError:
            raise

    try:
        check_call(['python', os.path.join(SPHINX_DIR, 'extract_rst.py')])
        check_call(['sphinx-build',
                    '-b', 'dirhtml',       # The used builder, either 'html' or 'dirhtml'
                    os.path.join(SPHINX_DIR, 'source/'),
                    os.path.join(BUILD_DIR, 'html')
                    ])
    except CalledProcessError as why:
        print("Coulnd't find path %s as defined in local_settings.py! " %
              SPHINX_DIR, why)
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(create_docs())
