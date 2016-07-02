#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.test import TestCase as DjangoTest, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
# NOCOMM: Not used, but should be replaced with python json because it gets removed in django 1.7
#from django.utils import simplejson as json
from wlmaps.models import *

import os

from settings import MEDIA_ROOT

elven_forests = os.path.dirname(__file__) + '/data/Elven Forests.wmf'

###########
# Helpers #
###########
class _LoginToSite(DjangoTest):
    def setUp(self):
        u = User.objects.create(username="root", email="root@root.com")
        u.set_password("root")
        u.save()

        self.client.login( username="root", password="root")

        self.user = u

#############
# TestCases #
#############
###########
# Uploads #
###########
class TestWLMaps_ValidUpload_ExceptCorrectResult(_LoginToSite):
    def runTest(self):
        url = reverse('wlmaps_upload')
        c = self.client.post(url, {'file': open(elven_forests,"rb"), 'test': True })

        o = Map.objects.get(pk=1)
        self.assertEqual(o.name, "Elven Forests")
        self.assertEqual(o.author, "Winterwind")
class TestWLMaps_AnonUpload_ExceptRedirect(DjangoTest):
    def runTest(self):
        url = reverse('wlmaps_upload')
        k = self.client.post(url, {'file': open(elven_forests,"rb") })
        self.assertRedirects( k, reverse('django.contrib.auth.views.login') + '?next=%s' %url )


# Invalid Uploading
class TestWLMaps_UploadWithoutMap_ExceptError(_LoginToSite):
    def runTest(self):
        url = reverse('wlmaps_upload')
        k = self.client.post(url, {'test': True })
        self.assertEqual(len(Map.objects.all()), 0)
class TestWLMaps_UploadTwice_ExceptCorrectResult(_LoginToSite):
    def runTest(self):
        url = reverse('wlmaps_upload')
        self.client.post(url, {'file': open(elven_forests,"rb"), 'test': True })
        self.assertEqual(len(Map.objects.all()), 1)

        self.client.post(url, {'file': open(elven_forests,"rb"), 'test': True })
        self.assertEqual(len(Map.objects.all()), 1)
class TestWLMaps_UploadWithInvalidMap_ExceptError(_LoginToSite):
    def runTest(self):
        url = reverse('wlmaps_upload')
        self.client.post(url, {'file': open(__file__,"rb"), 'test': True })
        self.assertEqual(len(Map.objects.all()), 0)

# Viewing
class TestWLMapsViews_Viewing(DjangoTest):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.user.save()

        # Add maps
        nm = Map.objects.create(
                        name = "Map",
                        author = "Author",
                        w = 128,
                        h = 64,
                        nr_players = 4,
                        descr = "a good map to play with",
                        minimap = "/wlmaps/minimaps/Map.png",
                        world_name = "blackland",

                        uploader = self.user,
                        uploader_comment = "Rockdamap"
        )
        nm.save()
        self.map = nm
        nm = Map.objects.create(
                        name = "Map with a long slug",
                        author = "Author Paul",
                        w = 128,
                        h = 64,
                        nr_players = 4,
                        descr = "a good map to play with",
                        minimap = "/wlmaps/minimaps/Map with long slug.png",
                        world_name = "blackland",

                        uploader = self.user,
                        uploader_comment = "Rockdamap"
        )
        nm.save()
        self.map1 = nm

    def test_ViewingValidMap_ExceptCorrectResult(self):
        c = self.client.get(reverse("wlmaps_view",args=("map-with-a-long-slug",)))
        self.assertEqual(c.status_code, 200 )
        self.assertEqual(c.context["object"], Map.objects.get(slug="map-with-a-long-slug"))
        self.assertTemplateUsed( c, 'wlmaps/map_detail.html' )

    def test_ViewingNonExistingMap_Except404(self):
        c = self.client.get(reverse("wlmaps_view",args=("a-map-that-doesnt-exist",)))
        self.assertEqual(c.status_code, 404 )


############
#  RATING  #
############
class TestWLMapsViews_Rating(_LoginToSite):
    def setUp(self):
        _LoginToSite.setUp(self)

        # Add maps
        nm = Map.objects.create(
                        name = "Map",
                        author = "Author",
                        w = 128,
                        h = 64,
                        nr_players = 4,
                        descr = "a good map to play with",
                        minimap = "/wlmaps/minimaps/Map.png",
                        world_name = "blackland",

                        uploader = self.user,
                        uploader_comment = "Rockdamap"
        )
        nm.save()
        self.map = nm

    def test_RatingNonExistingMap_Except404(self):
        c = self.client.post(
            reverse("wlmaps_rate",args=("a-map-that-doesnt-exist",)),
            { "vote": 10 } )
        self.assertEqual(c.status_code, 404 )

    def test_RatingGet_Except405(self):
        c = self.client.get(
            reverse("wlmaps_rate",args=("map",)),
            { "vote": 10 } )
        self.assertEqual(c.status_code, 405 )

    def test_RatingInvalidValue_Except400(self):
        c = self.client.post(
            reverse("wlmaps_rate",args=("map",)),
            { "vote": 11 } )
        self.assertEqual(c.status_code, 400 )

    def test_RatingNonIntegerValue_Except400(self):
        c = self.client.post(
            reverse("wlmaps_rate",args=("map",)),
            { "vote": "shubidu" } )
        self.assertEqual(c.status_code, 400 )

    def test_RatingExistingMap_ExceptCorrectResult(self):
        c = self.client.post(
            reverse("wlmaps_rate",args=("map",)),
            { "vote": 7 } )
        # Except redirect
        self.assertEqual(c.status_code, 302 )

        # We have to refetch this map, because
        # votes doesn't hit the database
        m = Map.objects.get(slug="map")

        self.assertEqual(m.rating.votes, 1)
        self.assertEqual(m.rating.score, 7)




