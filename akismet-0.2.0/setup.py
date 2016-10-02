#!/usr/bin/env python

from distutils.core import setup

import akismet

description = 'A Python interface to the Akismet anti comment-spam API.'
setup(name='akismet',
      version=akismet.__version__,
      description=description,
      author='Michael Foord',
      author_email='michael@voidspace.org.uk',
      url='http://www.voidspace.org.uk/python/modules.shtml#akismet',
      py_modules=['akismet'],
     )
