#!/usr/bin/env python
# encoding: utf-8

__all__ = ["MSError", "MSCriticalError", "MSGarbageError"]

class MSError(Exception):
    def __init__(self, *args):
        self.args = args
class MSCriticalError(MSError):
    def __init__(self, *args):
        self.args = args
class MSGarbageError(MSCriticalError):
    def __init__(self, *args):
        MSCriticalError.__init__(self, "GARBAGE_RECEIVED", *args)


