import os
import shutil
import sys
import tempfile
from unittest import mock

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from wlmaps.models import Map

# Stand-in for 'wl_map_info': the uploaded "map" is a text file whose content
# is the map name. 'fail' makes the tool exit with an error, 'hang' makes it
# sleep. The minimap gets the map name as content.
FAKE_MAP_INFO = """\
import json, sys, time

path = sys.argv[1]
with open(path) as f:
    name = f.read()
if name == "fail":
    sys.exit(1)
if name == "hang":
    time.sleep(30)
with open(path + ".png", "w") as f:
    f.write(name)
with open(path + ".json", "w") as f:
    json.dump(
        {
            "name": name,
            "author": "Author",
            "width": 64,
            "height": 64,
            "nr_players": 2,
            "description": "",
            "hint": "",
            "world_name": "",
            "minimum_required_widelands_version": "1.2",
            "minimap": path + ".png",
        },
        f,
    )
"""


class MapUploadProcessingTest(TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.media_root = os.path.join(self.tmp, "media")
        self.wl_dir = os.path.join(self.tmp, "widelands")
        os.mkdir(self.wl_dir)
        os.makedirs(os.path.join(self.media_root, "wlmaps", "minimaps"))
        tool = os.path.join(self.tmp, "wl_map_info")
        with open(tool, "w") as f:
            f.write(f"#!{sys.executable}\n{FAKE_MAP_INFO}")
        os.chmod(tool, 0o755)
        settings = override_settings(
            MEDIA_ROOT=self.media_root,
            WIDELANDS_SVN_DIR=self.wl_dir,
            WIDELANDS_MAP_INFO_TOOL=tool,
        )
        settings.enable()
        self.addCleanup(settings.disable)
        self.client.force_login(User.objects.create_user("mapper"))

    def _upload(self, content, filename="map.wmf"):
        return self.client.post(
            reverse("wlmaps_upload"),
            {"file": SimpleUploadedFile(filename, content.encode())},
        )

    def _minimap_content(self, name):
        with Map.objects.get(name=name).minimap.open("rb") as f:
            return f.read().decode()

    def test_maps_with_same_filename_keep_their_own_minimap(self):
        self._upload("First map")
        self._upload("Second map")

        self.assertEqual(Map.objects.count(), 2)
        self.assertEqual(self._minimap_content("First map"), "First map")
        self.assertEqual(self._minimap_content("Second map"), "Second map")

    def test_failing_tool_rejects_upload_and_keeps_working_directory(self):
        cwd = os.getcwd()
        response = self._upload("fail")

        self.assertContains(response, "The map file could not be processed.")
        self.assertEqual(os.getcwd(), cwd)
        self.assertFalse(Map.objects.exists())

    def test_hanging_tool_is_stopped(self):
        with mock.patch("wlmaps.forms.MAP_INFO_TIMEOUT", 1):
            response = self._upload("hang")

        self.assertContains(response, "The map file could not be processed.")
        self.assertFalse(Map.objects.exists())
