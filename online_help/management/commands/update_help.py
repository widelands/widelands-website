#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: update_help.py
#
# Created by Holger Rapp on 2009-02-26.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

from ...models import Worker as WorkerModel
from ...models import Tribe as TribeModel
from ...models import Ware as WareModel
from ...models import Building as BuildingModel

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from ConfigParser import ConfigParser, MissingSectionHeaderError
from glob import glob
import os
from os import path
import shutil
from cStringIO import StringIO
import re
from itertools import chain

from settings import MEDIA_ROOT, WIDELANDS_SVN_DIR, MEDIA_URL

from widelandslib.tribe import *
from widelandslib.make_flow_diagram import make_all_subgraphs

def normalize_name( s ):
    """
    Strips _ from the name endings
    """
    return s.strip('_')

class TribeParser(object):
    map_mouseover_pattern = re.compile(r'(?P<beginning>.*href="../../(?P<type>[^/]+)s/(?P<name>[^/]+)/".*")&lt;TABLE&gt;(?P<rest>.*)')
    def __init__(self, name):
        """
        Parses the definitions for one tribe and generates the models

        name - name of the tribe
        conf - path to the tribe/conf file
        """
        self._tribe = Tribe(name)
        # Generate the Tribe
        self._to = TribeModel.objects.get_or_create(name=name.lower())[0]
        self._to.displayname = normalize_name(self._tribe.name)
        self._to.save()

    def parse( self ):
        """Put all data into the database"""
        self._delete_old_media_dir()
        self._parse_workers()
        self._parse_wares()
        self._parse_buildings()

    def graph( self ):
        """Make all graphs"""
        tdir = make_all_subgraphs(self._tribe)
        for obj, cls in [(WorkerModel, "workers"),
                         (BuildingModel, "buildings"),
                         (WareModel, "wares")]:
            for inst in obj.objects.all().filter(tribe=self._to):
                try:
                    fpath = path.join(tdir,"help/%s/%s/%s/" % (self._tribe.name, cls, inst.name))
                    url = self._copy_picture(path.join(fpath, "image.png"), inst.name, "graph.png")
                    inst.graph_url = url
                    inst.imagemap = open(path.join(fpath, "map.map")).read()
                    inst.imagemap = self.map_mouseover_pattern.sub(r"\1Show the \2 \3\4", inst.imagemap)
                    inst.save()
                except Exception, e:
                    print "Exception while handling", cls, "of", self._tribe.name, ":", inst.name
                    print type(e), e, repr(e)
        
        shutil.rmtree(tdir)

    def _delete_old_media_dir(self):
        sdir = os.path.join(MEDIA_ROOT, "online_help", self._tribe.name)
        if os.path.exists(sdir):
            shutil.rmtree(sdir)

    def _copy_picture( self, file, name, fname ):
        """
        Copy the given image into the media directory

        file            - original path of image
        name            - name of the item (coal, iron...)
        fname           - file name of the picture
        """
        dn = "%s/online_help/img/%s/%s/" % (MEDIA_ROOT,self._to.name,name)
        try:
            os.makedirs(dn)
        except OSError, o:
            if o.errno != 17:
                raise
        new_name = path.join(dn, fname)
        shutil.copy(file, new_name )

        return "%s/%s" % (MEDIA_URL, new_name[len(MEDIA_ROOT):])

    def _parse_workers( self ):
        """Put the workers into the database"""
        print "  parsing workers"
        for worker in self._tribe.workers.values():
            print "    " + worker.name
            nn = self._copy_picture(worker.image, worker.name, "menu.png")

            workero = WorkerModel.objects.get_or_create( tribe = self._to, name = worker.name )[0]
            workero.displayname = normalize_name(worker.descname)
            workero.image_url = nn

            # See if there is help available
            if worker._conf.has_option("default","help"):
                helpstr = normalize_name(worker._conf.get("default","help"))
                workero.help = helpstr

            # Check for experience
            if worker._conf.has_option("default","experience"):
                experience = normalize_name(worker._conf.get("default","experience"))
                workero.exp = experience

            # See what the worker becomes
            try:
                enname = worker.becomes
                workero.becomes = WorkerModel.objects.get_or_create(
                        name=enname, tribe = self._to)[0]
            except:
                pass

            workero.save()

    def _parse_wares( self ):
        print "  parsing wares"
        for ware in self._tribe.wares.values():
            print "    " + ware.name
            nn = self._copy_picture(ware.image, ware.name, "menu.png")

            w = WareModel.objects.get_or_create( tribe = self._to, name = ware.name )[0]
            w.displayname = normalize_name(ware.descname)
            w.image_url = nn


            # See if there is help available
            if ware._conf.has_option("default","help"):
                helpstr = normalize_name(ware._conf.get("default","help"))
                w.help = helpstr

            w.save()

    def _parse_buildings( self ):
        def objects_with_counts(objtype, set_):
            counts = ' '.join(set_.values())
            objects = [objtype.objects.get_or_create(name = w, tribe = self._to)[0] for w in set_.keys()]
            return counts, objects

        enhancement_hier = []
        print "  parsing buildings"
        for building in self._tribe.buildings.values():
            print "    " + building.name
            b = BuildingModel.objects.get_or_create( tribe = self._to, name = building.name )[0]
            b.displayname = normalize_name(building.descname)
            b.type = building.btype

            # Get the building size
            size = building.size
            res, = [ k for k,v in BuildingModel.SIZES if v == size ]

            b.size = res

            nn = self._copy_picture(building.image, building.name, "menu.png" )
            b.image_url = nn

            # Try to figure out buildcost
            b.build_costs, b.build_wares = objects_with_counts(WareModel, building.buildcost)

            # Try to figure out who works there
            if isinstance(building, ProductionSite):
                b.workers_count, b.workers_types = objects_with_counts(WorkerModel, building.workers)

            # Try to figure out if this is an enhanced building
            if building.enhancement:
                enhancement_hier.append((b, building.enhancement))

            if building._conf.has_option("global","help"):
                helpstr = normalize_name(building._conf.get("global","help"))
                b.help = helpstr

            # See if there is any inputs field around
            if isinstance(building, ProductionSite):
                b.store_count, b.store_wares = objects_with_counts(WareModel, building.inputs)

                b.output_wares = [WareModel.objects.get_or_create(name = w, tribe = self._to)[0] for w in building.outputs]

            try:
                b.output_workers = [Worker.objects.get_or_create(name = w, tribe = self._to)[0] for w in building.recruits]
            except AttributeError:
                pass

            b.save()

        for b, tgt in enhancement_hier:
            try:
                b.enhancement = BuildingModel.objects.get(name = tgt, tribe = self._to)
            except Exception, e:
                raise
            b.save()

class Command(BaseCommand):
    help =\
    '''Reparses the conf files in a current checkout. '''

    def handle(self, directory = WIDELANDS_SVN_DIR, **kwargs):

        tribes = [d for d in glob("%s/tribes/*" % directory)
                    if os.path.isdir(d)]

        for t in tribes:
            tribename = os.path.basename(t)
            print "updating help for tribe ", tribename
            p = TribeParser(tribename)

            p.parse()
            p.graph()
