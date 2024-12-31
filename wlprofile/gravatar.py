try:
    from hashlib import md5
except ImportError:
    from md5 import md5
import os
import os.path
import warnings
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
from datetime import datetime, timedelta
import shutil
import socket

from pybb import settings as pybb_settings
from django.conf import settings

warnings.filterwarnings("ignore", r"tmpnam")


def fetch_gravatar(email):
    """Fetch avatar from gravatar.com service.

    Return None if avatar was not found.

    """

    hash = md5(email).hexdigest()
    size = max(pybb_settings.AVATAR_WIDTH, pybb_settings.AVATAR_HEIGHT)
    default = urllib.parse.quote("http://spam.egg/")

    url = "http://www.gravatar.com/avatar/%s?s=%d&d=%s" % (hash, size, default)
    fname = os.tmpnam()

    class RedirectHandler(urllib.request.HTTPRedirectHandler):
        def http_error_302(*args):
            raise IOError("Redirect found")

    timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(10)
    opener = urllib.request.build_opener(RedirectHandler())
    socket.setdefaulttimeout(timeout)

    try:
        file(fname, "wb").write(opener.open(url, fname).read())
    except IOError as ex:
        # logging.error(ex)
        return None
    else:
        return fname


def check_gravatar(user, ignore_date_joined=False, ignore_saved_avatar=False):
    if user.is_active:
        if ignore_date_joined or (datetime.now() - user.date_joined) < timedelta(
            seconds=3
        ):
            if ignore_saved_avatar or not user.pybb_profile.avatar:
                path = fetch_gravatar(user.email)
                if path:
                    avatars_dir = os.path.join(
                        settings.MEDIA_ROOT, pybb_settings.AVATARS_UPLOAD_TO
                    )
                    avatar_name = "_pybb_%d" % user.id

                    avatar_path = os.path.join(avatars_dir, avatar_name)
                    shutil.copy(path, avatar_path)

                    relpath = os.path.join(pybb_settings.AVATARS_UPLOAD_TO, avatar_name)
                    user.pybb_profile.avatar = relpath
                    user.pybb_profile.save()
                    return True
    return False
