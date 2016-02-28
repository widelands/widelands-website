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

import os
from os import makedirs, path
import shutil
import re
import json
import subprocess

from settings import MEDIA_ROOT, WIDELANDS_SVN_DIR, MEDIA_URL

from widelandslib.tribe import *
from widelandslib.make_flow_diagram import make_all_subgraphs

class TribeParser(object):
    map_mouseover_pattern = re.compile(r'(?P<beginning>.*href="../../(?P<type>[^/]+)s/(?P<name>[^/]+)/".*")&lt;TABLE&gt;(?P<rest>.*)')
    def __init__(self, name):
        """
        Parses the definitions for one tribe and generates the models

        name - name of the tribe
        """
        self._delete_old_media_dir(name) # You can deactivate this line if you don't need to clean house.

        base_directory = os.path.normpath(WIDELANDS_SVN_DIR + "/data")
        json_directory = os.path.normpath(base_directory + "/map_object_info")

        tribeinfo_file = open(os.path.normpath(json_directory + "/tribe_" + name + ".json"), "r")
        tribeinfo = json.load(tribeinfo_file)

        self._tribe = Tribe(tribeinfo, json_directory)
        # Generate the Tribe
        self._to = TribeModel.objects.get_or_create(name=name.lower())[0]
        self._to.displayname = tribeinfo['descname']
        self._to.descr = tribeinfo['tooltip']
        # copy icon
        dn = "%s/wlhelp/img/%s/" % (MEDIA_ROOT, tribeinfo['name'])
        try:
            os.makedirs(dn)
        except OSError, o:
            if o.errno != 17:
                raise
        new_name = path.join(dn, "icon.png")
        file = os.path.normpath(base_directory + "/" + tribeinfo['icon'])
        shutil.copy(file, new_name )
        self._to.icon_url = path.normpath("%s/%s" % (MEDIA_URL, new_name[len(MEDIA_ROOT):]))
        self._to.save()

    def parse( self, tribename, base_directory, json_directory ):
        """Put all data into the database"""
        self._delete_old_data(tribename) # You can deactivate this line if you don't need to clean house.

        wares_file = open(os.path.normpath(json_directory + "/" + tribename + "_wares.json"), "r")
        self._parse_wares(base_directory, json.load(wares_file))

        workers_file = open(os.path.normpath(json_directory + "/" + tribename + "_workers.json"), "r")
        self._parse_workers(base_directory, json.load(workers_file))

        buildings_file = open(os.path.normpath(json_directory + "/" + tribename + "_buildings.json"), "r")
        self._parse_buildings(base_directory, json.load(buildings_file))

    def graph( self ):
        """Make all graphs"""
        tdir = make_all_subgraphs(self._tribe)
        for obj, cls in [(WorkerModel, "workers"),
                         (BuildingModel, "buildings"),
                         (WareModel, "wares")]:
            for inst in obj.objects.all().filter(tribe=self._to):
                try:
                    fpath = path.join(tdir,"help/%s/%s/%s/" % (self._tribe.name, cls, inst.name))
                    url = self._copy_picture(path.join(fpath, "menu.png"), inst.name, "graph.png")
                    inst.graph_url = url
                    inst.imagemap = open(path.join(fpath, "map.map")).read()
                    inst.imagemap = self.map_mouseover_pattern.sub(r"\1Show the \2 \3\4", inst.imagemap)
                    inst.save()
                except Exception, e:
                    print "Exception while handling", cls, "of", self._tribe.name, ":", inst.name
                    print type(e), e, repr(e)

        shutil.rmtree(tdir)

    def _delete_old_media_dir(self, tribename):
		 """Clean house, e.g. when we have renamed a map object"""

		 print("Deleting old media files...");
		 sdir = os.path.join(MEDIA_ROOT, "wlhelp/img", tribename)
		 if os.path.exists(sdir):
			 shutil.rmtree(sdir)

    def _delete_old_data(self, tribename):
		 """Clean house, e.g. when we have renamed a map object"""

		 t = TribeModel.objects.get(name=tribename)
		 print("Deleting old wares...");
		 for ware in WareModel.objects.filter(tribe=t):
			ware.delete()
		 print("Deleting old workers...");
		 for worker in WorkerModel.objects.filter(tribe=t):
			worker.delete()
		 print("Deleting old buildings...");
		 for building in BuildingModel.objects.filter(tribe=t):
			building.delete()

    def _copy_picture( self, file, name, fname ):
        """
        Copy the given image into the media directory

        file            - original path of image
        name            - name of the item (coal, iron...)
        fname           - file name of the picture
        """
        dn = "%s/wlhelp/img/%s/%s/" % (MEDIA_ROOT,self._to.name,name)
        try:
            os.makedirs(dn)
        except OSError, o:
            if o.errno != 17:
                raise
        new_name = path.join(dn, fname)
        shutil.copy(file, new_name )

        return "%s/%s" % (MEDIA_URL, new_name[len(MEDIA_ROOT):])

    def _parse_workers( self, base_directory, workersinfo ):
        """Put the workers into the database"""
        print "  parsing workers"

        for worker in workersinfo['workers']:
            print "    " + worker['name']
            nn = self._copy_picture(os.path.normpath(base_directory + "/" + worker['icon']), worker['name'], "menu.png")

            workero = WorkerModel.objects.get_or_create( tribe = self._to, name = worker['name'] )[0]
            workero.displayname = worker['descname']
            workero.image_url = nn

            # Help
            workero.help = worker['helptext']

            # Check for experience
            if 'experience' in worker:
                workero.exp = worker['experience']

            # See what the worker becomes
            if 'becomes' in worker:
                try:
                    enname = worker.becomes
                    workero.becomes = WorkerModel.objects.get_or_create(
                            name=worker['becomes']['name'], tribe = self._to)[0]
                except:
                    pass

            workero.save()

    def _parse_wares( self, base_directory, waresinfo ):
        print "  parsing wares"

        for ware in waresinfo['wares']:
            print "    " + ware['name']
            nn = self._copy_picture(os.path.normpath(base_directory + "/" + ware['icon']), ware['name'], "menu.png")

            w = WareModel.objects.get_or_create( tribe = self._to, name = ware['name'] )[0]
            w.displayname = ware['descname']
            w.image_url = nn

            # Help
            w.help = ware['helptext']

            w.save()

    def _parse_buildings( self, base_directory, buildingsinfo ):
        def objects_with_counts(objtype, json_):
				element_set = {}
				for element in json_:
					element_set[element['name']] = str(element['amount'])
				counts = ' '.join(element_set.values())
				objects = [objtype.objects.get_or_create(name = w, tribe = self._to)[0] for w in element_set.keys()]
				return counts, objects

        enhancement_hierarchy = []
        print "  parsing buildings"

        for building in buildingsinfo['buildings']:
				print "    " + building['name']
				b = BuildingModel.objects.get_or_create( tribe = self._to, name = building['name'] )[0]
				b.displayname = building['descname']
				b.type = building['type']

				# Get the building size
				size = building['size']
				res, = [ k for k,v in BuildingModel.SIZES if v == size ]
				b.size = res

				nn = self._copy_picture(os.path.normpath(base_directory + "/" + building['icon']), building['name'], "menu.png")
				b.image_url = nn

				# Buildcost if we have any
				if 'buildcost' in building:
					b.build_costs, b.build_wares = objects_with_counts(WareModel, building['buildcost'])

				# Try to figure out who works there
				if 'workers' in building:
					b.workers_count, b.workers_types  = objects_with_counts(WorkerModel, building['workers'])

				# Try to figure out if this building can be enhanced
				if 'enhancement' in building:
					enhancement_hierarchy.append((b, building['enhancement']))

				b.help = building['helptext']

				# Input wares
				if 'stored_wares' in building:
					b.store_count, b.store_wares = objects_with_counts(WareModel, building['stored_wares'])

				# Output wares
				if 'produced_wares' in building:
					b.output_wares = [WareModel.objects.get_or_create(name = w, tribe = self._to)[0] for w in building['produced_wares']]

				# Output workers
				if 'produced_workers' in building:
					b.output_workers = [WorkerModel.objects.get_or_create(name = w, tribe = self._to)[0] for w in building['produced_workers']]

				b.save()

        for b, tgt in enhancement_hierarchy:
				try:
					b.enhancement = BuildingModel.objects.get(name = tgt, tribe = self._to)
				except Exception, e:
					raise
				b.save()

class Command(BaseCommand):
    help =\
    '''Regenerates and parses the json files in a current checkout. '''

    def handle(self, directory = os.path.normpath(WIDELANDS_SVN_DIR + "/data"), **kwargs):

        # First, we make sure that JSON files have been generated.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        is_json_valid = False
        os.chdir(WIDELANDS_SVN_DIR)
        try:
            subprocess.check_call(
                [os.path.normpath(WIDELANDS_SVN_DIR + "/build/src/logic/wl_map_object_info")])
        except:
            print("Error: Unable to execute 'wl_map_object_info' for generating the JSON files.")

        # Now we validate that they are indeed JSON files (syntax check only)
        try:
            subprocess.check_call(
                [os.path.normpath(WIDELANDS_SVN_DIR + "/utils/validate_json.py")])
            is_json_valid = True
        except:
            print("Error: JSON files are not valid.")

        os.chdir(current_dir)

        # We regenerate the encyclopedia only if the JSON files passed the syntax check
        if is_json_valid:
			  json_directory = os.path.normpath(directory + "/map_object_info")
			  source_file = open(os.path.normpath(json_directory + "/tribes.json"), "r")
			  tribesinfo = json.load(source_file)

			  for t in tribesinfo['tribes']:
			      tribename = t['name']
			      print "updating help for tribe ", tribename
			      p = TribeParser(tribename)
			      p.parse(tribename, directory, json_directory)
			      p.graph()
