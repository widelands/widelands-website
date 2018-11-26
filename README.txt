Installing the homepage
=======================

Getting the homepage to run locally is best supported using virtualenv and
pip. Install those two tools first, either via easy_install or via your local
package manager. You will also need development tools (gcc or therelike), hg
(mercurial), bzr, subversion and git. Finally you are going to need the
build dependencies for numpy, which will be compiled as a part of getting
the dependencies for the website. Go and install them all.

Example:
On Ubuntu, installing all required tools and dependencies in two commands:

   $ sudo apt-get install python-dev python-virtualenv python-pip mercurial bzr subversion git-core sqlite3
   $ sudo apt-get build-dep python-numpy

Used python version
-------------------

Currently, the website depends on python 2.7. In case you have python 3 as default (like on arch-linux),
you have to adjust the python relevant commands to use python 2.7. E.g. 'virtualenv2 wlwebsite' creates
a virtualenvironment using python 2.7. If the virtualenvironment is activated, python 2.7 will become
standard for executing python code in this shell.

Setting up the local environment
--------------------------------

Go to the directory you want to install the homepage to, then run:

   $ export PYTHONPATH=

This will make sure that your virtual environment is not tainted with python
packages from your global site packages. Very important!
Now, we create and activate our environment:

   $ virtualenv wlwebsite
   $ cd wlwebsite
   $ source bin/activate

Next, we download the website source code::

   $ mkdir code
   $ cd code
   $ bzr branch lp:widelands-website widelands
   $ cd widelands

All fine and good. Now we have to install all the third party modules the
website needs. We use pip for that.

Installation of the third party libraries should be easy, given you have
development tools installed and in your path. The two difficult packages are
PIL and numpy; you can also try to migrate them over from your global site dir
or add your global site dir to your PYTHONPATH.
Installation via pip should work like this::

   $ pip install -r pip_requirements.txt

This will take a while. If no errors are shown we should be fine.

Setting up the website
======================

Setting your local paths
------------------------

Copy or symlink the two files settings_local.py.sample and
local_urls.py.sample to settings_local.py and local_urls.py. Take a look at
those files and modify them to your needs - most likely everything works
directly, but you might want to edit the bd variable in local_settings.py::

   $ ln -s local_urls.py.sample local_urls.py
   $ ln -s local_settings.py.sample local_settings.py

Setting up the database
-----------------------

Now creating the tables in the database:

   $ ./manage.py migrate

Create a superuser:

   $ ./manage.py createsuperuser

Now, let's run the page::

   $ ./manage.py runserver

Open your browser to http://localhost:8000. You should see something that
resembles the widelands homepage quite closely. All content is missing though.

Some important settings
-----------------------

Go to http://localhost:8000/admin. Log in with your super user and go to the
following table:

- Site/Sites: Change your site name from example.com to localhost:8000.

Now everything should work.

Runnning with DBUG=False
------------------------
In case you want to test the site with the setting DEBUG=False, you might
notice that at least the admin site is missing all css. To fix this run:

  $ ./manage.py collectstatic -l

This will create symbolic links (-l) to static contents of third party apps in
the folder defined by STATIC_ROOT. See:
https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#collectstatic

Accessing the website from other machines
-----------------------------------------

When starting the server as described above, the website will by default
only be available from the machine it is running on. If you wish to access
the website from other machines you need to specify an IP-address and
port number. Please note, however, that this server is NOT intended for
production environments, only for development/testing.

   $ ./manage.py runserver 169.254.1.0:8000

See also https://docs.djangoproject.com/en/dev/ref/django-admin/#examples-of-using-different-ports-and-addresses
for further details.

Dependencies between website and widelands source code
======================================================

Some parts of the website need access to the source code of widelands:

* Online help/Encyclopedia
* Possibility to upload a map onto the local website
* Source code documentation

You will need the widelands source code for this, see

https://wl.widelands.org/wiki/BzrPrimer/

After the source code is downloaded, adjust the path of 

WIDELANDS_SVN_DIR

in local_settings.py to the path where the widelands source code is found.

Setting up the online help / encyclopedia
-----------------------------------------

You will need graphviz to generate the graphs for the online help. On Ubuntu run:

   $ sudo apt-get install graphviz

To generate the online help database switch to your local environment and run:

   $ ./manage.py update_help

After that you can create the overview pdf files with

   $ ./manage.py update_help_pdf

Setting up widelands source code documentation
----------------------------------------------

There is a small helper script to get the documenation. Be sure
you have set WIDELANDS_SVN_DIR set in local_settings.py. Run:

   $ ./manage.py create_docs

After finishing without errors, type localhost:8000/documentation/index.html
in your browsers addressbar or click on "Development -> Documentation".


Uploading a map to the local website
------------------------------------

Compile the widelands binaries by using the compile.sh script

   $ ./compile.sh

Now you should be able to upload a map onto your local website.

Contact
=======

Contact user 'kaputtnik' on the homepage for more information and problems.


-- vim:ft=rst:
