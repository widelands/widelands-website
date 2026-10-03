import json
import os
import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse


class DevelopersPageTest(TestCase):
    """The translator credits come from Transifex, so they must not be able
    to inject HTML into the developers page."""

    def setUp(self):
        wl_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, wl_dir)
        os.makedirs(os.path.join(wl_dir, "data", "i18n", "locales"))
        os.makedirs(os.path.join(wl_dir, "data", "txts"))
        self._write_json(
            wl_dir,
            "data/i18n/locales/xx.json",
            {
                "your-language-name-in-english": "Evil<script>alert(1)</script>",
                "translator-list": "Alice\n<img src=x onerror=alert(2)>",
            },
        )
        self._write_json(
            wl_dir,
            "data/txts/developers.json",
            {
                "developers": [
                    {"heading": "Translators", "entries": []},
                    {"heading": "Chieftains", "entries": [{"members": ["Bob"]}]},
                ]
            },
        )
        settings = override_settings(WIDELANDS_SVN_DIR=wl_dir + "/")
        settings.enable()
        self.addCleanup(settings.disable)

    def _write_json(self, wl_dir, name, data):
        with open(os.path.join(wl_dir, name), "w") as f:
            json.dump(data, f)

    def test_translator_credits_are_sanitized(self):
        response = self.client.get(reverse("developers"))

        self.assertContains(response, "Alice")
        self.assertContains(response, "Bob")
        self.assertNotContains(response, "<script>alert(1)")
        self.assertNotContains(response, "onerror")
