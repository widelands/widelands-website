Installing the homepage
=======================

Used python version
-------------------
The website is tested with python 3.10. This README reflects setting up the
website with this python version.

Framework versions
------------------
This project targets Django LTS (Long Term Support) releases for stability and
extended support. We currently use Django 5.2 LTS, which is supported until
April 2028. We will not upgrade to non-LTS versions.

Install prerequisites
---------------------

This project uses uv for dependency management. uv is a fast Python package
installer (10-100x faster than pip) that automatically manages a virtual
environment in .venv/ and ensures reproducible installs via lockfiles.

Install uv and system dependencies:

On Ubuntu:
   $ curl -LsSf https://astral.sh/uv/install.sh | sh
   $ sudo apt-get install git libmysqlclient-dev

On Mac:
   $ curl -LsSf https://astral.sh/uv/install.sh | sh
   $ brew install mysql libmagic


Setting up the local environment
--------------------------------

Clone the repository:

   $ git clone https://github.com/widelands/widelands-website widelands
   $ cd widelands

Install all dependencies (uv creates and manages the .venv/ automatically):

   $ uv sync

That's it! uv handles virtualenv creation, activation, and dependency
installation in one step. Dependencies are defined in pyproject.toml and
locked in uv.lock for reproducible builds.

To run commands in the virtual environment, prefix them with 'uv run':

   $ uv run ./manage.py runserver

Or activate the environment manually if preferred:

   $ source .venv/bin/activate


Setting up the website
======================

Setting your local paths
------------------------

Copy the two files settings_local.py.sample and local_urls.py.sample to
settings_local.py and local_urls.py inside the mainpage folder.
Take a look at those files and modify them to your needs - most likely
everything works directly, but you might want to edit the bd variable
in mainpage/local_settings.py::

   $ cp local_urls.py.sample mainpage/local_urls.py
   $ cp local_settings.py.sample mainpage/local_settings.py

Setting up the database
-----------------------

Now creating the tables in the database:

   $ uv run ./manage.py migrate
   $ uv run ./manage.py createcachetable

Create a superuser:

   $ uv run ./manage.py createsuperuser

Now, let's run the page:

   $ uv run ./manage.py runserver

Open your browser to http://localhost:8000. You should see something that
resembles the widelands homepage quite closely. All content is missing though.

Some important settings
-----------------------

Go to http://localhost:8000/admin. Log in with your super user and go to the
following table:

- Site/Sites: Change your site name from example.com to localhost:8000.

Now everything should work.

Runnning with DEBUG=False
-------------------------
In case you want to test the site with the setting DEBUG=False, you might
notice that at least the admin site is missing all css. To fix this run:

  $ uv run ./manage.py collectstatic -l

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

   $ uv run ./manage.py runserver 169.254.1.0:8000

See also https://docs.djangoproject.com/en/dev/ref/django-admin/#examples-of-using-different-ports-and-addresses
for further details.

Starting the website locally with gunicorn
------------------------------------------

This might be useful for testing thread-safety:

 $ cd mainpage
 $ gunicorn --workers 4 wlwebsite_wsgi:application

This will run the website with 4 workers (threads).

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
found. Then run:

   $ ./manage.py create_docs

After finishing without errors, type localhost:8000/documentation/index.html
in your browsers addressbar or click on "Development -> Documentation".

Widelands executables
---------------------

Widelands executables are needed to:

* Upload maps to the website
* Create the Encylopdia

Either install widelands as a program to your operating system, or create the
binaries by compiling the source code. If you want to compile, run:

   $ ./compile.sh -r

inside of the WIDELANDS_SVN_DIR to create a release build.

Uploading maps should work now.

Creating the encyclopdia needs graphviz to generate the graphs. On Ubuntu run:

   $ sudo apt-get install graphviz

To generate the online help switch to your local environment and run:

   $ ./manage.py update_help

Now you can create the economy graphs:

   $ ./manage.py update_help_pdf

You can access the encyclopdia by clicking on 'The Game -> Encyclopedia' now.

Dependencies between website and the addons server
==================================================

The addon-server is able to send emails for various actions in regard with
add-ons uploaded by users. The settings for emailing is done via a users
profile page on the website. In order to get this work locally you have to
set up the add-ons-server database and upload add-ons.
See: https://github.com/widelands/wl_addons_server for pointers

For a connection between the add-ons-server and the website define a new entry
in the DATABASES-section in local_settings.py called 'addonserver':

   'addonserver': {
        # Entries according to the add-on database
   }

Then define some notification-types in the admin page for WLADDONS_SETTINGS.
If a user has uploaded add-on(s) the noticetypes are created for this user if
he enters his profile page and clicks on the tab 'Add-On Settings'.

Known Dependency Issues
=======================

The following dependencies require attention for long-term maintenance:

**whoosh (2.7.4)** - Unmaintained since 2016. The search indexing library has not
been updated in over 10 years and poses security and compatibility risks. Consider
migrating to whoosh-reloaded (community fork), Elasticsearch, Meilisearch, or
Typesense when resources allow.

**bleach (6.3.0)** - Deprecated as of January 2023. While currently up-to-date,
this HTML sanitization library is no longer maintained. Consider migrating to nh3
or similar alternatives in the future.

**gunicorn (23.0.0)** - An update to 24.1.1 is available with security improvements
and ASGI support. The update requires testing in a staging environment due to
stricter HTTP parsing that may affect proxy setups.

Contact
=======

Contact user 'kaputtnik' on the homepage for more information and problems.

