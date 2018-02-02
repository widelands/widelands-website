#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Moves html files created by sphinx-build to the media directory

import os
import sys
import imp
import shutil

def get_settings():  
    # Didn't find a better way to get the settings from django
    f, path, descr = imp.find_module('../local_settings')
    settings = imp.load_module('local_settings', f, path, descr)
    f.close()
    
    return settings

def move_docs():
    settings = get_settings()
    WRITE_TO = os.path.join(settings.MEDIA_ROOT, 'documentation/')
    GET_FROM = os.path.join(settings.WIDELANDS_SVN_DIR, 'doc/sphinx/build/html')
    try:
        if os.path.exists(WRITE_TO):
            shutil.rmtree(WRITE_TO)
        shutil.copytree(GET_FROM, WRITE_TO)
    except (OSError, shutil.Error) as why:
        print("Something went wrong while moving files and directories", why)
        
if __name__ == '__main__':
    sys.exit(move_docs())
