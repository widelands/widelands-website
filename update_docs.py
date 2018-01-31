#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from subprocess import check_call, CalledProcessError
import os

GET_FROM = os.path.join(settings.WIDELANDS_SVN_DIR, 'doc/sphinx')
WRITE_TO = os.path.join(settings.MEDIA_ROOT,'documentation/')

def update_docs():
    
    try:
        # Extract rst snippets
        execfile(os.path.join(GET_FROM, "extract_rst.py"))
        # Create the documentation
        check_call(['sphinx-build',
                    '-b dirhtml -a -E -d ' +
                    os.path.join(WRITE_TO, '/doctrees ') +
                    os.path.join(GET_FROM, '/source ')
                    + WRITE_TO])
    except CalledProcessError:
        return 1
        
if __name__ == '__main__':
    sys.exit(update_docs())