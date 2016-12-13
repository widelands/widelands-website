#!/usr/bin/env python -tt
# encoding: utf-8
#

import sys
sys.path.append('..')

from numpy import *
import unittest
import base64
from cStringIO import StringIO
from itertools import *

from map import *

# General base class for tests that raise
# an exception


class _WLSetup(unittest.TestCase):

    def setUp(self):
        self.m = WidelandsMap()


# {{{ Elemental package
class _WLElemental_Base(unittest.TestCase):

    def setUp(self):
        self.m = WidelandsMap()
        self.m._read_elemental(StringIO(self.input))
#################
# Working Tests #
#################


class TestElementalReading_ValidInput_ExceptCorrectResult(_WLElemental_Base):
    # {{{ Data
    input = """[global]
packet_version=1
map_w=160
map_h=132
nr_players=4
world=greenland
name=_Elven Forests
author=Winterwind
descr=_"The breath-taking beauty of these ..."
"""
    # }}}

    def testDimensions(self):
        self.assertEqual(self.m.w, 160)
        self.assertEqual(self.m.h, 132)
        self.assertEqual(self.m.dim, (132, 160))

    def testNrPlayers(self):
        self.assertEqual(self.m.nr_players, 4)

    def testWorldName(self):
        self.assertEqual(self.m.world_name, 'greenland')

    def testName(self):
        self.assertEqual(self.m.name, 'Elven Forests')

    def testAuthor(self):
        self.assertEqual(self.m.author, 'Winterwind')

    def testDescr(self):
        self.assertEqual(self.m.descr, 'The breath-taking beauty of these ...')

##########
# Raises #
##########


class TestElementalReading_TestMissingSection_ExceptRaises(_WLSetup):
    # {{{ Data
    input = """[globalnoglbale]
blah = 1
"""
    # }}}

    def runTest(self):
        self.assertRaises(InvalidMapPackage, self.m._read_elemental,
                          StringIO(self.input))
# }}}

# {{{ Height package tests


class _WLHeight_Base(unittest.TestCase):

    def setUp(self):
        self.m = WidelandsMap()
        self.m._dim = self.dim
        self.m._read_heights(StringIO(self.input))


class _WLHeight_Setup(unittest.TestCase):

    def setUp(self):
        self.m = WidelandsMap()
        self.m._dim = self.dim
        self.input = StringIO(self.input)

#################
# Working Tests #
#################


class TestHeightReading_ValidInput_ExceptCorrectResult(_WLHeight_Base):
    # {{{ Data
    dim = (4, 6)  # w6, h4
    input = '\x01\x00)!\x08*\x0b1\x18-0\x1d\x03\x08.\x1e\x01\x19\x1f\x1d\x17\x17\x1c\x07#5'
    wanted = array([[41, 33,  8, 42, 11, 49],
                    [24, 45, 48, 29,  3,  8],
                    [46, 30,  1, 25, 31, 29],
                    [23, 23, 28,  7, 35, 53]])
    # }}}

    def runTest(self):
        self.assertTrue(all(self.wanted == self.m.heights))

##########
# Raises #
##########


class TestHeightReading_WrongVersion_ExceptRaises(_WLHeight_Setup):
    dim = (5, 7)
    input = '\x00\x02jdhf'

    def runTest(self):
        self.assertRaises(InvalidMapPackage, self.m._read_heights, self.input)


class TestHeightReading_PackageToShort_ExceptRaises(_WLHeight_Setup):
    dim = (5, 7)
    input = '\x01\x00jdhf'

    def runTest(self):
        self.assertRaises(InvalidMapPackage, self.m._read_heights, self.input)


class TestHeightReading_PackageToLong(_WLHeight_Setup):
    dim = (2, 2)
    input = '\x01\x00jdhkkf'

    def runTest(self):
        self.assertRaises(InvalidMapPackage, self.m._read_heights, self.input)
# }}}

# {{{ Terrain package tests


class _WLTerrain_Base(unittest.TestCase):

    def setUp(self):
        self.m = WidelandsMap()
        self.m._dim = self.dim
        self.m._read_terrains(StringIO(self.input))


class _WLTerrain_Setup(unittest.TestCase):

    def setUp(self):
        self.m = WidelandsMap()
        self.m._dim = self.dim
        self.input = StringIO(self.input)

#################
# Working Tests #
#################


class TestTerrainReading_ValidInput_ExceptCorrectResult(_WLTerrain_Base):
    # {{{ Data
    dim = (1, 2)  # w6, h4
    input = ('\x01\x00' +  # Package version
             '\x02\x00' +  # Nr of terrain types
             '\x00\x00Baum\x00\x01\x00Haus\x00' +  # Terrains (id,Name\x00)
             '\x01\x00\x00\x01'  # Terrain data (ter_r,ter_d)*nr_of_fields
             )
    ter_r_names = array([['Haus', 'Baum']])
    ter_d_names = array([['Baum', 'Haus']])
    # }}}

    def test_R(self):
        r = [i.name == j for i, j in izip(
            self.m.ter_r.flat, self.ter_r_names.flat)]
        self.assertTrue(all(r))

    def test_D(self):
        d = [i.name == j for i, j in izip(
            self.m.ter_d.flat, self.ter_d_names.flat)]
        self.assertTrue(all(d))

##########
# Raises #
##########


class TestTerrainReading_WrongVersion_ExceptRaises(_WLTerrain_Setup):
    dim = (5, 7)
    input = '\x00\x02jdhf'

    def runTest(self):
        self.assertRaises(InvalidMapPackage, self.m._read_terrains, self.input)


class TestTerrainReading_PackageToShort_ExceptRaises(_WLTerrain_Setup):
    dim = (5, 7)
    input = '\x01\x00jdhf'

    def runTest(self):
        self.assertRaises(InvalidMapPackage, self.m._read_terrains, self.input)


class TestTerrainReading_PackageToLong(_WLTerrain_Setup):
    dim = (1, 2)  # w6, h4
    input = ('\x01\x00' +  # Package version
             '\x02\x00' +  # Nr of terrain types
             '\x00\x00Baum\x00\x01\x00Haus\x00' +  # Terrains (id,Name\x00)
             # Terrain data (ter_r,ter_d)*nr_of_fields
             '\x02\x03\x04\x00\x00\x01'
             )
    ter_r_names = array([['Haus', 'Baum']])
    ter_d_names = array([['Baum', 'Haus']])

    def runTest(self):
        self.assertRaises(InvalidMapPackage, self.m._read_terrains, self.input)


class TestTerrainReading_WrongTerrainId(_WLTerrain_Setup):
    dim = (1, 2)  # w6, h4
    input = ('\x01\x00' +  # Package version
             '\x02\x00' +  # Nr of terrain types
             '\x00\x00Baum\x00\x01\x00Haus\x00' +  # Terrains (id,Name\x00)
             '\x00\x00\x02\x00'  # Terrain data (ter_r,ter_d)*nr_of_fields
             )

    def runTest(self):
        self.assertRaises(InvalidMapPackage, self.m._read_terrains, self.input)
# }}}
