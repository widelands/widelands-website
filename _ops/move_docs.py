#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Moves html files created by sphinx-build to the media directory

import os
import sys
import imp
import shutil

# Didn't find a better way to get the settings from django
f, path, descr = imp.find_module('../local_settings')
settings = imp.load_module('local_settings', f, path, descr)
f.close()

GET_FROM = os.path.join(settings.WIDELANDS_SVN_DIR, 'doc/sphinx/build/html')
WRITE_TO = os.path.join(settings.MEDIA_ROOT,'documentation/html')

def move_docs():
    try:
        shutil.copytree(GET_FROM, WRITE_TO)
    except shutil.Error:
        print("something went wrong while moving files and directories")
        
if __name__ == '__main__':
    sys.exit(move_docs())
