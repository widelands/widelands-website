#!/usr/bin/env python -tt
# encoding: utf-8
#

from conf import WidelandsConfigParser as Cp, NoOptionError, NoSectionError
from numpy import fromstring, array, empty, gradient
import struct
import os
import numpy
import zipfile
from cStringIO import StringIO
import Image

class Terrain(object):
    def __init__( self, name, id ):
        self._id = id
        self._name = name

    @property
    def name(self):
        return self._name
    @property
    def animation(self):
        return self._animation
    @property
    def id(self):
        return self._id

    def __repr__(self):
        return self._name


###########################################################################
#                                 ERRORS                                  #
###########################################################################
class WlMapLibraryException( Exception ): pass
class InvalidMapPackage( WlMapLibraryException ):
    def __init__(self, package_name, error ):
        self.pn = package_name
        self.error = error
    def __str__( self ):
        return "Error reading package %s: %s" % (self.pn,self.error)
class WlInvalidFile( WlMapLibraryException ): pass


class WidelandsMap(object):
    """
    This class parses a widelands map file as long as it is
    a directory (not a zip file).
    """
    def __init__(self, fn = None ):
        if fn is not None:
            self.load( fn )

#############
# FUNCTIONS #
#############
    def load( self, fn ):
        """
        Load a map from the given directory or zipfile

        fn - path to directory or zipfile or a file handle to the opened zipfile
        """

        if isinstance(fn,str) and os.path.isdir(fn):
            basedir = fn + '/'
            self._is_zip = False
            open_file = open
        else:
            self._is_zip = True
            try:
                zf = zipfile.ZipFile(fn)
            except zipfile.BadZipfile:
                raise WlInvalidFile()

            # Try to find elemental packet
            elementals = [ i.filename for i in zf.filelist if
               i.filename.find("elemental") != -1 and
               i.filename.find('.svn') == -1]

            if len(elementals) != 1:
                # Try to use the one called 'elemental'
                elementals = [ e for e in elementals if os.path.basename(e) == "elemental" ]
                if len(elementals) != 1:
                    raise WlInvalidFile("Map contains an invalid number of elemental packets")
            el = elementals[0].rsplit('/')
            if len(el) == 1:
                basedir = ''
            else:
                basedir = el[0] + '/'

            open_file = lambda fn,mode: StringIO(zf.read(fn))

        # Okay, try to read our files
        self._read_elemental( open_file(basedir + 'elemental','r') )
        self._read_heights( open_file(basedir + 'binary/heights','rb') )
        self._read_terrains( open_file(basedir + 'binary/terrain', 'rb') )

##############
# Properties #
##############
    @property
    def dim(self):
        "Map dimensions (h,w). Not: height first! like in numpy"
        return self._dim
    @property
    def w(self):
        return self._dim[1]
    @property
    def h(self):
        return self._dim[0]

    @property
    def nr_players(self):
        "Nr of players"
        return self._nr_players
    @property
    def world_name(self):
        "Name of world"
        return self._world_name
    @property
    def name(self):
        "Name of map"
        return self._name
    @property
    def author(self):
        "The maps creator"
        return self._author
    @property
    def descr(self):
        "The maps description"
        return self._descr

    @property
    def heights(self):
        "The heights of the various fields, an 2d array: a[y,x]"
        return self._heights

    @property
    def ter_r(self):
        "The RO foo property."
        return self._terr
    @property
    def ter_d(self):
        "The RO foo property."
        return self._terd
    @property
    def terrains(self):
        "The RO foo property."
        return self._terrains


###########################################################################
#                   PRIVATE PARSING FUNCTIONALITY BELOW                   #
###########################################################################
    def _read_elemental(self, file):
        def error(m):
            raise InvalidMapPackage("elemental", m)
        cp =Cp( file )

        try:
            version = cp.getint("global","packet_version")
            if version != 1:
                error("Invalid package version: %i" % version)

            self._dim = cp.getint("global","map_h"), cp.getint("global","map_w")
            self._nr_players = cp.getint("global","nr_players")
            self._world_name = cp.getstring("global", "world")
            self._name = cp.getstring("global", "name")
            self._author = cp.getstring("global", "author")
            self._descr = cp.getstring("global", "descr")
        except NoOptionError,e:
            error("Missing option: %s:%s" % (e.section,e.option))
        except NoSectionError,e:
            error("Missing section: %s" % (e.section,))

          # TODO: background picture

    def _read_heights(self, file):
        def error(m):
            raise InvalidMapPackage("heights", m)
        s = file.read()
        version, = struct.unpack_from("<H",s)
        if version != 1:
            error("Invalid package version: %i" % version)
        if len(s) != self._dim[0]*self._dim[1] + 2:
            error("Package has wrong length.")
        self._heights = fromstring(s[2:],dtype="u1").reshape(self._dim)

    def _read_terrains(self, file):
        def error(m):
            raise InvalidMapPackage("terrain", m)
        s = file.read()
        version, = struct.unpack_from("<H",s)
        if version != 1:
            error("Invalid package version: %i" % version)

        try:
            nrterrains, = struct.unpack_from("<H",s,2)
        except struct.error:
            error("Package has wrong length.")

        terrains = [None] * nrterrains
        nread = 4
        for i in range(nrterrains):
            try:
                tid, = struct.unpack_from("<H",s,nread)
            except struct.error:
                error("Package has wrong length.")
            if tid >= nrterrains:
                error("Invalid terrain id in package-header")

            nread += 2
            name = s[nread:s.find("\x00",nread)]
            nread += len(name)+1

            terrains[tid] = Terrain( name, tid )

        self._terrains = terrains
        a = fromstring(s[nread:],dtype="u1")

        if len(a) != self._dim[0]*self._dim[1]*2:
            error("Package has wrong length.")

        try:
            self._terr = numpy.empty( self._dim[0]*self._dim[1], dtype="object")
            self._terr[:] = [ terrains[o] for o in a[::2] ]
            self._terr.shape =  self._dim
            self._terd = numpy.empty( self._dim[0]*self._dim[1], dtype="object")
            self._terd[:] = [ terrains[o] for o in a[1::2] ]
            self._terd.shape =  self._dim
        except IndexError:
            error("Invalid terrain index in package.")

    def make_minimap( self, datadir ):
        """
        Returns an RGB minimap of the map.

        datadir - Path to widelands directory so that the texture can be read
        """
        # Read the terrains
        colors = [None]* len(self._terrains)
        for t in self._terrains:
            i = Image.open(datadir + '/worlds/' + self._world_name + '/pics/' + t.name + '_00.png').convert("RGB")
            i = fromstring(i.tostring(),dtype="uint8").reshape( (64,64,3))
            colors[ t.id ] = i.mean(axis=0).mean(axis=0)

        # Make the minimap
        mm = empty( (self._dim)+ (3,), dtype = "uint8" )
        for y in range(self._dim[0]):
            for x in range(self._dim[1]):
                t = self._terr[y,x]
                mm[y,x] = colors[t.id]

        # Now, add the heights
        rubbish,dx = gradient(self._heights.astype("float64"))
        dx -= dx.min()
        if dx.max():
            dx /= dx.max()
        dx *= 255.
        rdx = empty( (self._dim)+(3,), dtype="float64")
        rdx[:,:,0] = dx
        rdx[:,:,1] = dx
        rdx[:,:,2] = dx
        dx = rdx

        # This is taken from the gimps overlay functionality
        # see here:
        # http://docs.gimp.org/en/gimp-concepts-layer-modes.html
        mm = mm / 255. * (mm + 2 * dx / 255. * (255. - mm))

        return mm.astype("uint8")




