This directory contains the widelands homepage django project. It needs a bunch of third party applications. A (maybe not complete list) is here:

* atomformat.py
* diff_match_patch.py
* django-messages
* django-notification
* django-pagination
* django-registration
* django-tagging
* django-simplestats
* django-comment_utils
* django-threadedcomments

# Installation

Most of these subprojects have dependencies on their own. Install all of them.
Then put this directory and it's direct parent into your PYTHONPATH, create a
local_settings.py file with (at least) your database settings and launch the
testserver:

$ ./manage.py runserver


