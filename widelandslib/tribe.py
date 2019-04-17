#!/usr/bin/env python
# encoding: utf-8

import os.path as p
import json
try:
    from django.conf import settings
    basedir = settings.WIDELANDS_SVN_DIR
except:
    basedir = p.join(p.dirname(__file__), p.pardir, p.pardir)


class BaseDescr(object):

    def __init__(self, tribe, name, descname, json):
        self.tribe = tribe
        self._json = json
        self.name = name
        self.descname = descname

    @property
    def image(self):
        return p.abspath(p.join(settings.WIDELANDS_SVN_DIR, 'data', self._json['icon']))


class Ware(BaseDescr):

    def __str__(self):
        return 'Ware(%s)' % self.name


class Worker(BaseDescr):

    @property
    def becomes(self):
        if 'becomes' in self._json:
            return self._json['becomes']['name']
        else:
            return None

    def __str__(self):
        return 'Worker(%s)' % self.name


class Building(BaseDescr):

    @property
    def enhanced_building(self):
        if 'enhanced' in self._json:
            return True
        else:
            return False

    @property
    def base_building(self):
        if not self.enhanced_building:
            return None
        bases = [b for b in list(self.tribe.buildings.values())
                 if b.enhancement == self.name]
        if len(bases) == 0 and self.enhanced_building:
            raise Exception('Building %s has no bases in tribe %s' %
                            (self.name, self.tribe.name))
        if len(bases) > 1:
            raise Exception('Building %s seems to have more than one base in tribe %s.' % (
                self.name, self.tribe.name))
        return bases[0]

    @property
    def enhancement(self):
        if 'enhancement' in self._json:
            return self._json['enhancement']
        else:
            return None

    @property
    def buildcost(self):
        result = dict()
        if 'buildcost' in self._json:
            for buildcost in self._json['buildcost']:
                result[buildcost['name']] = buildcost['amount']
        return result

    @property
    def size(self):
        return self._json['size']


class ProductionSite(Building):
    btype = 'productionsite'

    @property
    def outputs(self):
        result = set()
        if 'produced_wares' in self._json:
            for warename in self._json['produced_wares']:
                result.add(warename)
        return result

    @property
    def inputs(self):
        result = dict()
        if 'stored_wares' in self._json:
            for ware in self._json['stored_wares']:
                result[ware['name']] = ware['amount']
        return result

    @property
    def workers(self):
        result = dict()
        if 'workers' in self._json:
            for worker in self._json['workers']:
                result[worker['name']] = worker['amount']
        return result

    @property
    def recruits(self):
        result = set()
        if 'produced_workers' in self._json:
            for workername in self._json['produced_workers']:
                result.add(workername)
        return result


class Warehouse(Building):
    btype = 'warehouse'
    pass


class TrainingSite(ProductionSite):
    btype = 'trainingsite'
    pass


class MilitarySite(Building):
    btype = 'militarysite'

    @property
    def conquers(self):
        return self._json['conquers']

    @property
    def max_soldiers(self):
        return self._json['max_soldiers']

    @property
    def heal_per_second(self):
        return self._json['heal_per_second']


class Tribe(object):

    def __init__(self, tribeinfo, json_directory):
        self.name = tribeinfo['name']

        wares_file = open(p.normpath(json_directory + '/' +
                                     self.name + '_wares.json'), 'r')
        waresinfo = json.load(wares_file)
        self.wares = dict()
        for ware in waresinfo['wares']:
            descname = ware['descname']
            self.wares[ware['name']] = Ware(self, ware['name'], descname, ware)

        workers_file = open(p.normpath(
            json_directory + '/' + self.name + '_workers.json'), 'r')
        workersinfo = json.load(workers_file)
        self.workers = dict()
        for worker in workersinfo['workers']:
            descname = worker['descname']
            self.workers[worker['name']] = Worker(
                self, worker['name'], descname, worker)

        buildings_file = open(p.normpath(
            json_directory + '/' + self.name + '_buildings.json'), 'r')
        buildingsinfo = json.load(buildings_file)
        self.buildings = dict()
        for building in buildingsinfo['buildings']:
            descname = building['descname']
            if building['type'] == 'productionsite':
                self.buildings[building['name']] = ProductionSite(
                    self, building['name'], descname, building)
            elif building['type'] == 'warehouse':
                self.buildings[building['name']] = Warehouse(
                    self, building['name'], descname, building)
            elif building['type'] == 'trainingsite':
                self.buildings[building['name']] = TrainingSite(
                    self, building['name'], descname, building)
            elif building['type'] == 'militarysite':
                self.buildings[building['name']] = MilitarySite(
                    self, building['name'], descname, building)
            else:
                self.buildings[building['name']] = Building(
                    self, building['name'], descname, building)

    def __str__(self):
        return 'Tribe(%s)' % self.name
