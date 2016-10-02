#!/usr/bin/python
# Version 0.1.2
# 2005/12/05

# Copyright Michael Foord 2005
# test_akismet.py
# Test CGI for akismet.py - the Python interface to the akismet API

# http://www.voidspace.org.uk/python/modules.shtml
# http://akismet.com

# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/python/license.shtml

# For information about bugfixes, updates and support, please join the Pythonutils mailing list.
# http://groups.google.com/group/pythonutils/
# Comments, suggestions and bug reports welcome.
# Scripts maintained at http://www.voidspace.org.uk/python/index.shtml
# E-mail fuzzyman@voidspace.org.uk

"""
A simple test CGI for akismet.py

Requires cgiutils and a file called apikey.txt
"""

import cgi
import os
import sys
import cgitb
cgitb.enable()

sys.path.append('../modules')
sys.path.append('modules')

from cgiutils import *
import akismet
from akismet import Akismet

__version__ = '0.1.2'

DEBUG = False

valuelist = ['comment', 'comment_author_email', 'comment_author',
    'comment_author_url', ]

header = '''<html><head><title>Akismet Test CGI</title></head><body>
<center><h1>Testing the Python Interface to Akismet</h1>
By 
<em><a href="http://www.voidspace.org.uk/python/index.shtml">Fuzzyman</a></em>
<br><br>
<h2>Combatting Comment Spam</h2>
<h2>Akismet Test Version %s</h2>
<a href="http://www.voidspace.org.uk/python/modules.shtml#akismet">
<h2>Python API Version %s</h2></a>
''' % (__version__, akismet.__version__)

form = '''
**result**
<em>Posts With the Name set as </em><strong>viagra-test-123</strong>
<em>Should Always be Marked as Spam</em><br>
<strong>Enter a comment to test :</strong>
<form method="post" action="**scriptname**">
    <table>
        <tr><td align="right"><small><strong><label for="comment_author">Your Name:</label></strong></small></td>
            <td><input type="text" name="comment_author" value ="**comment_author**" ></td></tr>
        <tr><td align="right"><small><strong><label for="comment_author_email">Your E-Mail Address:</label></strong></small></td>
            <td><input type="text" name="comment_author_email" size="40" value="**comment_author_email**" ></td></tr>

        <tr><td align="right"><small><strong><label for="comment_author_url">Homepage:</label></strong></small></td>
            <td><input type="text" name="comment_author_url" value="**comment_author_url**" size="40"></td></tr>
    </table><br>
    <small><strong><label for="comment">Please make your comments below</label></strong></small><br>
    <textarea name="comment" cols="60" rows="6" wrap="hard">**comment**</textarea>
    <br><br>
    <input type="submit" value="Go For It"><input type="reset">
</form>
'''

footer = '</center></body></html>'

no_key = '''<h1>This script needs a %sWordpress API Key</h1>
<h2><a href="http://wordpress.com">Vist Wordpress</a></h2>
'''

res_line = '<h1>Akismet Says the Comment is %s</h1>'

def results(req):
    #
    # FIXME: could break here if apikey.txt exists, but has no key/blog_url
    api = Akismet()
    if api.key is None:
        # apikey.txt file
        return no_key % ''
    if not api.verify_key():
        # invalid key
        return no_key % 'Valid '
    # check the form - it contains some relevant data
    # the rest will be filled in with defaults
    for entry, val in os.environ.items():
        if entry.startswith('HTTP'):
            req[entry] = val
    result = api.comment_check(req['comment'], req, DEBUG=DEBUG)
    if DEBUG:
        return res_line % result
    elif result:
        return res_line % 'Spam'
    else:
        return res_line % 'Ham'

def main():
    # getrequest, serverline, cgiprint, replace - all come from cgituils
    req = getrequest(valuelist)
    cgiprint(serverline)
    cgiprint()
    print header
    #
    if req['comment'].strip():
        result = '<br><br>%s<br><br>' % results(req)
    else:
        req['comment_author'] = 'viagra-test-123'
        result = ''
    rep = {'**result**': result }
    for key, val in req.items():
        rep['**%s**' % key] = val.strip()
    rep['**scriptname**'] = os.environ['SCRIPT_NAME']
    print replace(form, rep)
    print footer


if __name__ == '__main__':
    if not 'SCRIPT_NAME' in os.environ:
        print 'This script must be run as a CGI'
    else:
        main()

"""

CHANGELOG
=========

2005/12/05      Version 0.1.2
-----------------------------

Added DEBUG mode


2005/12/04      Version 0.1.1
-----------------------------

Added the version numbers

Added default name 'viagra-test-123'


2005/12/02      Version 0.1.0
-----------------------------

A simple test script for akismet.py

It tests ``verify_key`` and ``comment_check`` in 80 lines of code

"""