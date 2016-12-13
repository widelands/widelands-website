import os
import sys

parent_dir = lambda dir: os.path.abspath(os.path.join(dir, os.pardir))

code_directory = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))

current_dir = code_directory
activate_this = None
while current_dir != '/':
    current_dir = parent_dir(current_dir)
    if os.path.exists(os.path.join(current_dir, 'bin', 'activate_this.py')):
        activate_this = os.path.join(current_dir, 'bin', 'activate_this.py')
        break

if activate_this is None:
    raise RuntimeException('Could not find virtualenv to start up!')

execfile(activate_this, dict(__file__=activate_this))

sys.path.append(parent_dir(code_directory))
sys.path.append(code_directory)
sys.path.append(os.path.join(code_directory, 'widelands'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'widelands.settings'

if os.path.exists('/usr/games'):
    os.environ['PATH'] += ':/usr/games'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
