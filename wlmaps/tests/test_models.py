#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.test import TestCase as DjangoTest
from django.db import IntegrityError
from django.contrib.auth.models import User
from wlmaps.models import Map


#############
# TestCases #
#############


class TestWLMapsModels_Map(DjangoTest):
    urls = "wlmaps.test_urls"

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

    def test_validMapInsertion_expectCorrectResult(self):
        # This really tests the setUp functionality. let's
        # hope that this worked out
        self.assertEqual(Map.objects.get(author="Author"), self.map)

    def test_MapNameGeneration_expectCorrectResult(self):
        self.assertEqual(repr(self.map), "<Map: Map by Author>")

    def test_Permalink_expectCorrectResult(self):
        self.assertEqual(self.map.get_absolute_url(), "/maps/map/")
        self.assertEqual(self.map1.get_absolute_url(), "/maps/map-with-a-long-slug/")

    def test_DoubleAddingMapWithSameSlug_ExceptRaise(self):
        self.assertRaises(
            IntegrityError,
            Map.objects.create,
            **{
                "name": "Map with-a-long slug",
                "author": "Author",
                "w": 128,
                "h": 64,
                "nr_players": 4,
                "descr": "a good map to play with",
                "minimap": "/wlmaps/minimaps/Map.png",
                "world_name": "blackland",
                "uploader": self.user,
                "uploader_comment": "Rockdamap",
            },
        )

    def test_DoubleAddingMapWithSameName_ExceptRaise(self):
        self.assertRaises(
            IntegrityError,
            Map.objects.create,
            **{
                "name": "Map",
                "slug": "something-other",
                "author": "Author",
                "w": 128,
                "h": 64,
                "nr_players": 4,
                "descr": "a good map to play with",
                "minimap": "/wlmaps/minimaps/Map.png",
                "world_name": "blackland",
                "uploader": self.user,
                "uploader_comment": "Rockdamap",
            },
        )
