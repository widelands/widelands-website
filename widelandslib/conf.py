#!/usr/bin/env python -tt
# encoding: utf-8

from ConfigParser import *
import cStringIO

__all__ = [
    "WidelandsConfigParser"
]

def clear_string(s):
    idx = s.find('#')
    if idx != -1:
        s = s[:idx]

    s = s.strip("'\" _")
    return s

class WidelandsConfigParser(SafeConfigParser):
    def __init__(self, fn):
        """
        Basically we only add one option: getstring which removes
        ticks and '_' (the translation marker)
        """
        SafeConfigParser.__init__(self)

        string = ""
        try:
            string = fn.read()
        except AttributeError:
            string = open(fn, "r").read()

        try:
            self.readfp(cStringIO.StringIO(string))
        except MissingSectionHeaderError:
            string = '[global]\n' + string
            self.readfp(cStringIO.StringIO(string))


    def items(self, *args, **kwargs):
        return dict(
            (k,clear_string(v)) for (k,v) in
               SafeConfigParser.items(self, *args, **kwargs)
        ).items()

    def getstring( self, s, opt, default = None):
        try:
            return clear_string(self.get(s,opt))
        except NoOptionError:
            if default is not None:
                return default
            raise

    def getint( self, s, opt, default = None):
        try:
            return SafeConfigParser.getint(self,s,opt)
        except NoOptionError:
            if default is not None:
                return default
            raise
        except ValueError:
            return int(clear_string(SafeConfigParser.get(self,s,opt)))

    def getboolean( self, s, opt, default = None):
        try:
            return SafeConfigParser.getboolean(self,s,opt)
        except NoOptionError:
            if default is not None:
                return default
            raise

