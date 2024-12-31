#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.test import TestCase as DjangoTest
from django.contrib.auth.models import User
from wlmaps.models import Map
from django.urls import reverse
import os

elven_forests = os.path.dirname(__file__) + "/data/Elven Forests.wmf"

###########
# Helpers #
###########


class _LoginToSite(DjangoTest):
    def setUp(self):
        u = User.objects.create(username="root", email="root@root.com")
        u.set_password("root")
        u.save()

        self.client.login(username="root", password="root")

        self.user = u


#############
# TestCases #
#############
###########
# Uploads #
###########


class TestWLMaps_ValidUpload_ExceptCorrectResult(_LoginToSite):
    def runTest(self):
        url = reverse("wlmaps_upload")
        with open(elven_forests, "rb") as f:
            c = self.client.post(url, {"file": f, "test": True})

        o = Map.objects.get(name="Elven Forests")
        self.assertEqual(o.name, "Elven Forests")
        self.assertEqual(o.author, "Winterwind")


class TestWLMaps_AnonUpload_ExceptRedirect(DjangoTest):
    def runTest(self):
        url = reverse("wlmaps_upload")
        with open(elven_forests, "rb") as f:
            k = self.client.post(url, {"file": f})
        self.assertRedirects(k, "/accounts/login/?next=/maps/upload/")


# Invalid Uploading
class TestWLMaps_UploadWithoutMap_ExceptError(_LoginToSite):
    def runTest(self):
        url = reverse("wlmaps_upload")
        k = self.client.post(url, {"test": True})
        self.assertEqual(len(Map.objects.all()), 0)


class TestWLMaps_UploadTwice_ExceptCorrectResult(_LoginToSite):
    def runTest(self):
        url = reverse("wlmaps_upload")
        with open(elven_forests, "rb") as f:
            self.client.post(url, {"file": f, "test": True})
        self.assertEqual(len(Map.objects.all()), 1)

        with open(elven_forests, "rb") as f:
            self.client.post(url, {"file": f, "test": True})
        self.assertEqual(len(Map.objects.all()), 1)


class TestWLMaps_UploadWithInvalidMap_ExceptError(_LoginToSite):
    def runTest(self):
        url = reverse("wlmaps_upload")
        with open(__file__, "rb") as f:
            self.client.post(url, {"file": f, "test": True})
        self.assertEqual(len(Map.objects.all()), 0)


# Viewing


class TestWLMapsViews_Viewing(DjangoTest):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.user.save()

        # Add maps
        nm = Map.objects.create(
            name="Map",
            author="Author",
            w=128,
            h=64,
            nr_players=4,
            descr="a good map to play with",
            minimap="/wlmaps/minimaps/Map.png",
            world_name="blackland",
            uploader=self.user,
            uploader_comment="Rockdamap",
        )
        nm.save()
        self.map = nm
        nm = Map.objects.create(
            name="Map with a long slug",
            author="Author Paul",
            w=128,
            h=64,
            nr_players=4,
            descr="a good map to play with",
            minimap="/wlmaps/minimaps/Map with long slug.png",
            world_name="blackland",
            uploader=self.user,
            uploader_comment="Rockdamap",
        )
        nm.save()
        self.map1 = nm

    def test_ViewingValidMap_ExceptCorrectResult(self):
        c = self.client.get(reverse("wlmaps_view", args=("map-with-a-long-slug",)))
        self.assertEqual(c.status_code, 200)
        self.assertEqual(
            c.context["object"], Map.objects.get(slug="map-with-a-long-slug")
        )
        self.assertTemplateUsed(c, "wlmaps/map_detail.html")

    def test_ViewingNonExistingMap_Except404(self):
        c = self.client.get(reverse("wlmaps_view", args=("a-map-that-doesnt-exist",)))
        self.assertEqual(c.status_code, 404)
