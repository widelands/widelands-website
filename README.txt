This directory contains the widelands homepage django project. It needs a bunch of third party applications. A (maybe not complete list) is here:

* atomformat.py
    http://code.google.com/p/django-notification/
    in /notification/atomformat.py
* diff_match_patch.py
    http://code.google.com/p/google-diff-match-patch/
    in /python/diff_match_patch.py
* django-messages
    http://code.google.com/p/django-messages/
* django-notification
    http://code.google.com/p/django-notification/
* django-pagination
    http://code.google.com/p/django-pagination/
* django-registration
    http://bitbucket.org/ubernostrum/django-registration/wiki/Home
* django-tagging
    http://code.google.com/p/django-tagging/
* django-simplestats
    http://code.google.com/p/django-simplestats/
* django-comment_utils
    http://code.google.com/p/django-comment-utils/
* django-threadedcomments
    http://code.google.com/p/django-threadedcomments/
* djangosphinx (for search)
    http://django-sphinx.googlecode.com/p/django-sphinx/
* django-tracking
    http://code.google.com/p/django-tracking/

# Installation

Most of these subprojects have dependencies on their own. Install all of them.
Then put this directory and it's direct parent into your PYTHONPATH, create a
local_settings.py file with (at least) your database settings and launch the
testserver:

$ ./manage.py runserver


