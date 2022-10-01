#!/usr/bin/env python -tt
# encoding: utf-8
#

import sys

sys.path.append("..")

from nose.tools import *

from tribe import Tribe


class TestTribe(object):
    def setUp(self):
        self.b = Tribe("barbarians")
        self.e = Tribe("empire")
        self.a = Tribe("atlanteans")

    def test_produces(self):
        assert_equal(
            ["axe", "battleaxe", "broadaxe", "bronzeaxe", "sharpaxe", "warriorsaxe"],
            self.b.buildings["warmill"].outputs,
        )

    def test_enhancement(self):
        assert_equal("warmill", self.b.buildings["axefactory"].enhancement)

    def test_enhanced_building(self):
        assert_equal(True, self.b.buildings["warmill"].enhanced_building)
        assert_equal(False, self.b.buildings["lumberjacks_hut"].enhanced_building)
