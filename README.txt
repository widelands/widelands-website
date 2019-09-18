Installing the homepage
=======================

Used python version
-------------------
The website is tested with python 3.6. This README reflects setting up the
website with this python version.

Install prerequisites
---------------------

Getting the homepage to run locally is best supported using virtualenv and
pip. Install those two tools first, either via easy_install or via your local
package manager. You will also need development tools, subversion or git.
Finally you are going to need the build dependencies for numpy, which will be
compiled as a part of getting the dependencies for the website.
Go and install them all.

Example:
On Ubuntu, installing all required tools and dependencies in two commands::

   sudo apt-get install python3-virtualenv python3-pip git subversion libmysqlclient-dev
   sudo apt-get build-dep python3-numpy

Setting up the local environment
--------------------------------

Go to the directory you want to install the homepage to, then run::

   export PYTHONPATH=

This will make sure that your virtual environment is not tainted with python
packages from your global site packages. Very important!
Now, we create and activate our environment::

   virtualenv --python=python3.6 wlwebsite
   cd wlwebsite
   source bin/activate

Next, we download the website source code::

   mkdir code
   cd code
   git clone https://github.com/widelands/widelands-website.git widelands
   cd widelands

All fine and good. Now we have to install all the third party modules the
website needs. We use pip for that.

Installation of the third party libraries should be easy, given you have
development tools installed and in your path. The two difficult packages are
PIL and numpy; you can also try to migrate them over from your global site dir
or add your global site dir to your PYTHONPATH.
Installation via pip should work like this::

   pip install -r pip_requirements.txt

This will take a while. If no errors are shown we should be fine.


Setting up the website
======================

Setting your local paths
------------------------

Copy or symlink the two files settings_local.py.sample and
local_urls.py.sample to settings_local.py and local_urls.py. Take a look at
those files and modify them to your needs - most likely everything works
directly, but you might want to edit the bd variable in local_settings.py::

   ln -s local_urls.py.sample mainpage/local_urls.py
   ln -s local_settings.py.sample mainpage/local_settings.py

Setting up the database
-----------------------

Create the tables in the database::

   ./manage.py migrate
   ./manage.py createcachetable

Create a superuser::

   ./manage.py createsuperuser

Now, let's run the page::

   ./manage.py runserver

Open your browser to http://localhost:8000. You should see something that
resembles the widelands homepage quite closely. All content is missing though.

Some important settings
-----------------------

Go to http://localhost:8000/admin. Log in with your super user and go to the
section "Site->Sites" and change your site name from example.com to
localhost:8000.

Now everything should work.

Runnning with DBUG=False
------------------------
In case you want to test the site with the setting DEBUG=False, you might
notice that at least the admin site is missing all css. To fix this run::

  ./manage.py collectstatic -l

This will create symbolic links (-l) to static contents of third party apps in
the folder defined by STATIC_ROOT. See:
https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#collectstatic

Accessing the website from other machines
-----------------------------------------

See https://docs.djangoproject.com/en/dev/ref/django-admin/#examples-of-using-different-ports-and-addresses
for further details.


Dependencies between website and widelands source code
======================================================

Some parts of the website need access to the source code of widelands, other 
parts need some widelands executables.

Source code only
----------------

The documentation is made out of the source code. To get a copy, see:

https://wl.widelands.org/wiki/GitPrimer/

After the source code is downloaded, adjust the path of 

WIDELANDS_SVN_DIR = '/path/to/widelands/trunk'

in mainpage/local_settings.py to the path where the widelands source code can be
found. Then run::

   ./manage.py create_docs

After finishing without errors, type localhost:8000/documentation/index.html
in your browsers addressbar or click on "Development -> Documentation".

Widelands executables
---------------------

Widelands executables are needed to:

* Upload maps to the website
* Create the Encylopdia

Either install widelands as a program to your operating system, or create the 
binaries by compiling the source code. If you want to compile, run::

   ./compile.sh -r

inside of the WIDELANDS_SVN_DIR to create a release build.

Uploading maps should work now.

Creating the encyclopdia needs graphviz to generate the graphs. On Ubuntu run::

   sudo apt-get install graphviz

To generate the online help switch to the local environment of the website
and run::

   ./manage.py update_help

Now you can create the economy graphs::

   ./manage.py update_help_pdf

You can access the encyclopdia by clicking on 'The Game -> Encyclopedia' now.


Contact
=======

Contact user 'kaputtnik' on the homepage for more information and problems.

-- vim:ft=rst:
