#!/usr/bin/env python
# encoding: utf-8

from conf import WidelandsConfigParser
from ConfigParser import NoSectionError, NoOptionError
import conf
from itertools import chain
import os.path as p
import re
from string import replace
try:
    from settings import WIDELANDS_SVN_DIR
    basedir = WIDELANDS_SVN_DIR
except:
    basedir = p.join(p.dirname(__file__), p.pardir, p.pardir)

class BaseDescr(object):
    def __init__(self, tribe, name, descname, tdir):
        self.tribe = tribe
        self._tdir = tdir
        self._conf_file = p.join(tdir, name, "conf")
        self._conf = WidelandsConfigParser(p.join(tdir,name,"conf"))

        self.name = name
        self.descname = descname

    @property
    def image(self):
        return p.abspath(p.join(self._tdir,self.name,"menu.png"))

class Ware(BaseDescr):
    def __str__(self):
        return "Ware(%s)" % self.name

class Worker(BaseDescr):
    @property
    def outputs(self):
        rv = set(sorted(
            i.strip() for i in re.findall(r'\d+=\s*createitem\s*(\w+)',
                open(self._conf_file).read())
        ))
        return rv

    @property
    def becomes(self):
        try:
            return self._conf.get("global", "becomes")
        except NoOptionError:
            return None

    def __str__(self):
        return "Worker(%s)" % self.name

class Building(BaseDescr):
    @property
    def enhanced_building(self):
        return self._conf.getboolean("global", "enhanced_building", False)

    @property
    def base_building(self):
        if not self.enhanced_building:
            return None
        bases = [b for b in self.tribe.buildings.values() if b.enhancement == self.name]
        if len(bases) == 0 and self.enhanced_building:
            raise Exception("Building %s has no bases in tribe %s" % (self.name, self.tribe.name))
        if len(bases) > 1:
            raise Exception("Building %s seems to have more than one base in tribe %s." % (self.name, self.tribe.name))
        return bases[0]

    @property
    def enhancement(self):
        rv = self._conf.getstring("global", "enhancement", "none")
        return rv if rv != "none" else None

    @property
    def image(self):
        glob_pat = self._conf.getstring("idle", "pics")
        return p.abspath(p.join(self._tdir,self.name,replace(glob_pat,'?','0')))

    @property
    def buildcost(self):
        try:
            return dict(self._conf.items("buildcost"))
        except NoSectionError:
            return {}

    @property
    def size(self):
        return self._conf.getstring("global", "size")

class ProductionSite(Building):
    btype = "productionsite"
    @property
    def outputs(self):
        self_produced = set(sorted(
            i.strip() for i in re.findall(r'produce\s*=\s*(\w+)',
                open(self._conf_file).read())
        ))
        if not len(self_produced):
            rv = reduce(lambda a,b: a | b, [ self.tribe.workers[w].outputs
                    for w in self.workers ], set())
            return rv
        return self_produced

    @property
    def inputs(self):
        try:
            return dict( (k, v) for k,v in self._conf.items("inputs") )
        except conf.NoSectionError:
            return dict()

    @property
    def workers(self):
        return dict( (k, v) for k,v in self._conf.items("working positions") )

    @property
    def recruits(self):
        recs = set([])
        for prog,_ in self._conf.items("programs"):
            recs |= set([name for type, name in self._conf.items(prog) if type == "recruit"])
        return recs

class Warehouse(Building):
    btype = "warehouse"
    pass

class TrainingSite(ProductionSite):
    btype = "trainings site"
    pass

class MilitarySite(Building):
    btype = "military site"
    @property
    def conquers(self):
        return self._conf.get("global", "conquers")

    @property
    def max_soldiers(self):
        return self._conf.get("global", "max_soldiers")

    @property
    def heal_per_second(self):
        return self._conf.getint("global", "heal_per_second")


class Tribe(object):
    def __init__(self, name, bdir = basedir):
        self.name = name

        # NOCOM self._tdir = p.join(bdir, "tribes", name)

        # NOCOM self._conf = WidelandsConfigParser(p.join(self._tdir, "conf"))

        # NOCOM self.wares = dict( (k,Ware(self, k, v, self._tdir)) for k,v in
        # NOCOM     self._conf.items("ware types"))
        # NOCOM self.workers = dict(chain(
        # NOCOM     ((k,Worker(self, k, v, self._tdir)) for k,v in
        # NOCOM         self._conf.items("worker types")),
        # NOCOM     ((k,Worker(self, k, v, self._tdir)) for k,v in
        # NOCOM         self._conf.items("carrier types")),
        # NOCOM ))


        # NOCOM self.buildings = dict(chain(
        # NOCOM     ((k,ProductionSite(self, k, v, self._tdir)) for k,v in \
        # NOCOM         self._conf.items("productionsite types")),
        # NOCOM     ((k,MilitarySite(self, k, v, self._tdir)) for k,v in \
        # NOCOM         self._conf.items("militarysite types")),
        # NOCOM     ((k,Warehouse(self, k, v, self._tdir)) for k,v in \
        # NOCOM         self._conf.items("warehouse types")),
        # NOCOM     ((k,TrainingSite(self, k, v, self._tdir)) for k,v in \
        # NOCOM         self._conf.items("trainingsite types")),
        # NOCOM ))

    def __str__(self):
        return "Tribe(%s)" % self.name


