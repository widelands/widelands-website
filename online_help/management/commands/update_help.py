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

from ...models import Ware, Tribe, Building

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from ConfigParser import ConfigParser, MissingSectionHeaderError
from glob import glob
import os
import shutil
from cStringIO import StringIO
import re

from settings import MEDIA_ROOT, WIDELANDS_SVN_DIR

class SaneConfigParser(ConfigParser):
    def read(self,f):
        s = open(f).read()
        s = s.strip()
        s = re.subn(r'#.*','',s)[0] # remove comments
        try:
            sio = StringIO(s)
            rv = ConfigParser.readfp(self,sio)
        except MissingSectionHeaderError:
            s = "[default]\n"+s
            sio = StringIO(s)
            rv = ConfigParser.readfp(self,sio)
            
        self._string = s

    @property
    def string(self):
        return self._string


def normalize_name( s ):
    """
    Strips _ from the name endings
    """
    return s.strip('_')

class TribeParser(object):
    def __init__(self,name, conf):
        """
        Parses the definitions for one tribe and generates the models
    
        name - name of the tribe
        conf - path to the tribe/conf file
        """
        self._cf = SaneConfigParser()
        self._cf.read(conf)
        
        # Generate the Tribe
        self._to = Tribe.objects.get_or_create(name=name.lower())[0]
        self._to.displayname = normalize_name(self._cf.get("tribe","name"))
        self._to.save()

        self._basedir = os.path.dirname(conf)

    def parse( self ):
        self._parse_wares()
        self._parse_buildings()

    def _copy_picture( self, file, name, fname ):
        """
        Copy the given image into the media directory
        
        file            - original path of image
        name            - name of the item (coal, iron...)
        fname           - file name of the picture
        """
        dn = "%s/online_help/img/%s/%s/" % (MEDIA_ROOT,self._to.name,name)
        try:
            if os.path.exists(dn):
                shutil.rmtree(dn)
            os.makedirs(dn)
        except OSError, o:
            if o.errno != 17:
                raise
        new_name = dn + '/' + fname
        shutil.copy(file, new_name )
        return new_name[len(MEDIA_ROOT):]
    
    def _parse_wares( self ):
        items = self._cf.items("ware types")
        for name,displayname in items:
            mp = "%s/%s/menu.png" % (self._basedir,name)
            nn = self._copy_picture(mp,name, "menu.png" )
            
            w = Ware.objects.get_or_create( tribe = self._to, name = name )[0]
            w.displayname = normalize_name(displayname)
            w.image_url = nn 

            # See if there is help available
            if self._cf.has_option("default","help"):
                helpstr = normalize_name(self._cf.get("default","help"))
                w.help = helpstr

            w.save()
    
    def _parse_buildings( self ):
        def _parse_common( name, displayname, type ):
            def _parse_item_with_counts( cf, section ):
                counts = []
                wares = [] 
                for ware,count in cf.items(section):
                    wares.append(ware)
                    counts.append(count)
                w = [ Ware.objects.get( tribe = self._to, name = ware.lower()) for ware in wares ]
                return w, counts

            conf = "%s/%s/conf" % (self._basedir,name)
            cf = SaneConfigParser()
            cf.read(conf)
            
            b = Building.objects.get_or_create( tribe = self._to, name = name )[0]
            b.displayname = normalize_name(displayname)
            b.type = type 
            
            # Get the building size
            size = cf.get("default","size")
            res, = [ k for k,v in Building.SIZES if v == size ]

            b.size = res

            # Try to figure out idle picture
            idle_pattern =cf.get("idle","pics").split()[0] if cf.has_option("idle","pics") else "idle*png"
            glob_files = glob( self._basedir + '/' + name + '/' + idle_pattern)
            picpath = glob_files[0]
            nn = self._copy_picture(picpath,name, "idle.png" )
            b.image_url = nn

            # Try to figure out buildcost
            if cf.has_section("buildcost"):
                w,counts = _parse_item_with_counts(cf,"buildcost")
                b.build_costs = ' '.join(counts)
                b.build_wares = w

            # Try to figure out if this is an enhanced building
            if cf.has_option("default","enhancement"):
                enname = cf.get("default","enhancement")
                b.enhancement = Building.objects.get_or_create( name=enname, tribe = self._to )[0]

            # See if there is help available
            if cf.has_option("default","help"):
                helpstr = normalize_name(cf.get("default","help"))
                b.help = helpstr

            # See if there is any inputs field around
            if cf.has_section("inputs"):
                w,counts = _parse_item_with_counts(cf,"inputs")
                b.store_count = ' '.join(counts)
                b.store_wares = w
            
            # Check for outputs
            outputs = []
            for line in cf.string.split('\n'):
                line = line.strip()
                if line.startswith("output"):
                    outputs.append( line.split("=")[-1].strip() )
            if len(outputs):
                w = [ Ware.objects.get( tribe = self._to, name = ware.lower()) for ware in outputs ]
                b.output_wares = w


            return b

        for secname,type in [
            ("productionsite types","P"),
            ("trainingsite types","T"),
            ("militarysite types","M"),
            ("warehouse types","W") ]:
            items = self._cf.items(secname)
            for name,displayname in items:
                b = _parse_common( name, displayname, type )
                b.save()

            

class Command(BaseCommand):
    help =\
    '''Reparses the conf files in a current checkout. '''

    def handle(self, directory = WIDELANDS_SVN_DIR, **kwargs):

        tribes = [ d for d in glob("%s/tribes/*" % directory) if os.path.isdir(d) ]
        
        for t in tribes:
            tribename = os.path.basename(t)
            p = TribeParser(tribename,t+'/conf')
            
            p.parse()
        


