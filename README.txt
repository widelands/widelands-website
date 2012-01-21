Installing the homepage
=======================

Getting the homepage to run locally is best supported using virtualenv and
pip. Install those two tools first, either via easy_install or via your local
package manager. You will also need development tools (gcc or therelike), hg
(mercurial), bzr, subversion and git. Finally you are going to need the
build dependencies for numpy, which will be compiled as a part of getting
the dependencies for the website. Go and install them all.

Example:
On Ubuntu, installing all required tools and dependencies in two commands::

   $ sudo apt-get install python-dev python-virtualenv python-pip mercurial bzr subversion git-core sqlite3
   $ sudo apt-get build-dep python-numpy

Setting up the local environment
--------------------------------

Go to the directory you want to install the homepage to, then run::

   $ export PYTHONPATH=

This will make sure that your virtual environment is not tainted with python
packages from your global site packages. Very important!
Now, we create our environment and download the website::

   $ virtualenv --no-site-packages wlwebsite
   $ cd wlwebsite
   $ mkdir code
   $ cd code
   $ bzr branch lp:widelands-website widelands

All fine and good. Now we have to install all the third party modules the
website needs. We use pip for that. But first, we have to change into our
local environment::

   $ cd .. # Now, we are in the root dir of our environemnt
   $ source bin/activate

Installation of the third party libraries should be easy, given you have
development tools installed and in your path. The two difficult packages are
PIL and numpy; you can also try to migrate them over from your global site dir
or add your global site dir to your PYTHONPATH. 
Installation via pip should work like this::

   $ pip -E . install -r code/widelands/pip_requirements.txt

This will take a while. If no errors are shown we should be fine. 

Setting up the website
----------------------

Go back into the widelands bzr directory::

   $ cd code/widelands

Setting your local paths
^^^^^^^^^^^^^^^^^^^^^^^^

Copy or symlink the two files settings_local.py.sample and
local_urls.py.sample to settings_local.py and local_urls.py. Take a look at
those files and modify them to your needs - most likely everything works
directly, but you might want to edit the bd variable in local_settings.py::

   $ ln -s local_urls.py.sample local_urls.py
   $ ln -s local_settings.py.sample local_settings.py

Setting up the database
^^^^^^^^^^^^^^^^^^^^^^^

Now, let's try if everything works out::

   $ ./manage.py syncdb

You will need to enter a superuser name and account. Now, let's run the page::

   $ ./manage.py runserver

Open your browser to http://localhost:8000. You should see something that
resembles the widelands homepage quite closely. All content is missing though. 

Some important settings
^^^^^^^^^^^^^^^^^^^^^^^

Go to http://localhost:8000/admin. Log in with your super user and go to the
Sites Admin. Change your site name from example.com to localhost. Now,
everything should work out.

Accessing the website from other machines
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When starting the server as described above, the website will by default
only be available from the machine it is running on. If you wish to access
the website from other machines you need to specify an IP-address and
port number. Please note, however, that this server is NOT intended for
production environments, only for development/testing.

   $ ./manage.py runserver 169.254.1.0:8000

See also http://docs.djangoproject.com/en/dev/ref/django-admin/#runserver-port-or-address-port
for further details. 

Contact
=======

Contact SirVer on the homepage for more information and problems.


-- vim:ft=rst:
