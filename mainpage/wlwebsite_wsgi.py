import os
import sys

# Run gunicorn from the project's virtualenv (uv's `.venv/bin/gunicorn`);
# the interpreter then already has the right site-packages.
parent_dir = lambda dir: os.path.abspath(os.path.join(dir, os.pardir))

code_directory = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(parent_dir(code_directory))
sys.path.append(code_directory)
sys.path.append(os.path.join(code_directory, "widelands"))

os.environ["DJANGO_SETTINGS_MODULE"] = "mainpage.settings"

if os.path.exists("/usr/games"):
    os.environ["PATH"] += ":/usr/games"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
