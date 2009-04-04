#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.test import TestCase as DjangoTest, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import simplejson as json
from wlmaps.models import *

import os

from settings import MEDIA_ROOT

elven_forests = os.path.dirname(__file__) + '/data/Elven Forests.wmf'

print "contains ipython embed code!"
from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed()

###########
# Helpers #
###########
class _LoginToSite(DjangoTest):
    def setUp(self):
        u = User.objects.create(username="root", email="root@root.com")
        u.set_password("root")
        u.save()
        
        self.client.login( username="root", password="root")

#############
# TestCases #
#############
###########
# Uploads #
###########
class TestWLMaps_ValidUpload_ExceptCorrectResult(_LoginToSite):
    def runTest(self):
        url = reverse('wlmaps_upload')
        k = self.client.post(url, {'mapfile': open(elven_forests,"rb"), 'test': True })
        rv = json.loads( k.content )
        self.assertEqual(rv["success_code"], 0)
        self.assertEqual(rv["map_id"], 1)

        o = Map.objects.get(pk=1)
        self.assertEqual(o.name, "Elven Forests")
        self.assertEqual(o.author, "Winterwind")
class TestWLMaps_AnonUpload_ExceptRedirect(DjangoTest):
    def runTest(self):
        url = reverse('wlmaps_upload')
        k = self.client.post(url, {'mapfile': open(elven_forests,"rb") })
        self.assertRedirects( k, reverse('django.contrib.auth.views.login') + '?next=%s' %url )
class TestWLMaps_UploadGet_ExceptNotAllowed(_LoginToSite):
    def runTest(self):
        k = self.client.get(reverse('wlmaps_upload'))
        self.assertEqual( k.status_code, 405 )
        self.assertEqual( k["allow"], 'post' )

# Invalid Uploading
class TestWLMaps_UploadWithoutMap_ExceptError(_LoginToSite):
    def runTest(self):
        url = reverse('wlmaps_upload')
        k = self.client.post(url, {'test': True })
        rv = json.loads( k.content )
        self.assertEqual(rv["success_code"], 1)
class TestWLMaps_UploadTwice_ExceptCorrectResult(_LoginToSite):
    def runTest(self):
        url = reverse('wlmaps_upload')
        k = self.client.post(url, {'mapfile': open(elven_forests,"rb"), 'test': True })
        rv = json.loads( k.content )
        self.assertEqual(rv["success_code"], 0)
        self.assertEqual(rv["map_id"], 1)
        
        k = self.client.post(url, {'mapfile': open(elven_forests,"rb"), 'test': True })
        rv = json.loads( k.content )
        self.assertEqual(rv["success_code"], 2)
class TestWLMaps_UploadWithInvalidMap_ExceptError(_LoginToSite):
    def runTest(self):
        url = reverse('wlmaps_upload')
        k = self.client.post(url, {'mapfile': open(__file__,"rb"), 'test': True })
        rv = json.loads( k.content )
        self.assertEqual(rv["success_code"], 3)
       
# Viewing, listing
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



