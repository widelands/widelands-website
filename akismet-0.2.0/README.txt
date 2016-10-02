# Version 0.2.0
# Copyright Michael Foord 2005-2009
# akismet.py
# Python interface to the akismet API
# E-mail fuzzyman@voidspace.org.uk

# http://www.voidspace.org.uk/python/modules.shtml#akismet
# http://akismet.com

# Released subject to the BSD License
# See http://www.voidspace.org.uk/python/license.shtml

A python interface to the `Akismet <http://akismet.com>`_ API.
This is a web service for blocking SPAM comments to blogs - or other online 
services.

You will need a Wordpress API key, from `wordpress.com <http://wordpress.com>`_.

You should pass in the keyword argument 'agent' to the name of your program,
when you create an Akismet instance. This sets the ``user-agent`` to a useful
value.

The default is : ::

    Python Interface by Fuzzyman | akismet.py/0.2.0

Whatever you pass in, will replace the *Python Interface by Fuzzyman* part.
**0.2.0** will change with the version of this interface.

Usage example::
    
    from akismet import Akismet
    
    api = Akismet(agent='Test Script')
    # if apikey.txt is in place,
    # the key will automatically be set
    # or you can call api.setAPIKey()
    #
    if api.key is None:
        print "No 'apikey.txt' file."
    elif not api.verify_key():
        print "The API key is invalid."
    else:
        # data should be a dictionary of values
        # They can all be filled in with defaults
        # from a CGI environment
        if api.comment_check(comment, data):
            print 'This comment is spam.'
        else:
            print 'This comment is ham.'

As of version 0.2.0 akismet.py can be used with Google AppEngine.