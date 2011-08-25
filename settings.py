# Django settings for widelands project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'dev.db'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/wlmedia/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '#*bc7*q0-br42fc&6l^x@zzk&(=-#gr!)fn@t30n54n05jkqcu'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    # 'simplestats.middleware.RegexLoggingMiddleware',
    'django.middleware.gzip.GZipMiddleware', # Remove this, when load gets to high
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'tracking.middleware.VisitorTrackingMiddleware',
    'tracking.middleware.VisitorCleanUpMiddleware',
)

ROOT_URLCONF = 'widelands.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/var/www/django_projects/widelands/templates',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
)

############################
# Activation configuration #
############################
DEFAULT_FROM_EMAIL = 'noreply@widelands.org'
ACCOUNT_ACTIVATION_DAYS=2 # Days an activation token keeps active

######################
# Wiki configuration #
######################
WIKI_LOCK_DURATION = 30

######################
# User configuration #
######################
AUTH_PROFILE_MODULE = 'wlprofile.Profile'
DEFAULT_TIME_ZONE = 3
DEFAULT_MARKUP ="markdown"
SIGNATURE_MAX_LENGTH = 255
SIGNATURE_MAX_LINES = 8
AVATARS_UPLOAD_TO = "profile/avatars"
AVATAR_HEIGHT  = AVATAR_WIDTH = 80

######################
# Pybb Configuration #
######################
PYBB_ATTACHMENT_ENABLE = False
PYBB_DEFAULT_MARKUP = 'markdown'

##############################################
# Link classification and other Markup stuff #
##############################################
LOCAL_DOMAINS = [
    "xoops.widelands.org"
]
SMILEY_DIR = MEDIA_URL + "img/smileys/"
# Keep this list ordered by length of smileys
SMILEYS = [
    ("O:-)", "face-angel.png"),
    (":'-(", "face-crying.png"),
    ("&gt;:-)", "face-devilish.png"), # Hack around markdown replacement. see also SMILEY_PREESCAPING
    (":(|)", "face-monkey.png"),
    (":-D", "face-grin.png"),
    ("8-)", "face-glasses.png"),
    (":-x", "face-kiss.png"),
    (":-|", "face-plain.png"),
    (":-(", "face-sad.png"),
    (":))", "face-smile-big.png"),
    (":-)", "face-smile.png"),
    (":-O", "face-surprise.png"),
    (";-)", "face-wink.png"),
    (":D", "face-grin.png"),
    (":(", "face-sad.png"),
    (":)", "face-smile.png"),
    (":O", "face-surprise.png"),
    (";)", "face-wink.png"),
]
# This needs to be done to keep some stuff hidden from markdown
SMILEY_PREESCAPING = [
    (">:-)", "\>:-)"),
]

###############################
# Sphinx (Search prog) Config #
###############################
USE_SPHINX=False
SPHINX_API_VERSION = 0x116

############
# Tracking #
############
TRACKING_CLEANUP_TIMEOUT=48

###########################
# Widelands SVN directory #
###########################
# This is needed for various thinks, for example
# to access media (for minimap creation) or for online help
# or for ChangeLog displays
WIDELANDS_SVN_DIR=""

#####################
# ChangeLog display #
#####################
BZR_URL = r"http://bazaar.launchpad.net/%%7Ewidelands-dev/widelands/trunk/revision/%s"

###############
# Screenshots #
###############
THUMBNAIL_SIZE = ( 160, 160 )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.humanize',

    # TODO: only temporary for webdesign stuff
    'django.contrib.webdesign',

    # Thirdparty apps, but need preload
    'tracking',

    # Our own apps
    'widelands.mainpage',
    'widelands.online_help',
    'widelands.wlimages',
    'widelands.wlwebchat',
    'widelands.wlrecaptcha',
    'widelands.wlprofile',
    'widelands.wlsearch',
    'widelands.wlpoll',
    'widelands.wlevents',
    'widelands.wlmaps',
    'widelands.wlscreens',
    'widelands.wlggz',

    # Modified 3rd party apps
    'widelands.wiki', # This is based on wikiapp, but has some local modifications
    'widelands.news', # This is based on simple-blog, but has some local modifications
    'pybb', # Feature enriched version of pybb

    # Thirdparty apps
    'threadedcomments',
    'django_messages',
    'registration', # User registration (per Email validation)
    'pagination',
    'tagging',
    'notification',
    'djangoratings',
    'sphinxdoc',
    'django_evolution',
)

try:
    from local_settings import *
except ImportError:
    pass

if USE_SPHINX:
    INSTALLED_APPS += (
        'djangosphinx',
    )
