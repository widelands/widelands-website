#!/usr/bin/env python
# encoding: utf-8

__all__ = ["make_packet", "Packet"]

from wlms.errors import MSGarbageError

class Packet(object):
    def __init__(self, args):
        """Convenience wrapper around a received packet"""
        self._args = args

    def string(self):
        try:
            return self._args.pop(0)
        except IndexError:
            raise MSGarbageError("Wanted a string but got no arguments left")

    def int(self):
        s = self.string()
        try:
            return int(s)
        except ValueError:
            raise MSGarbageError("Invalid integer: %r" % s)

    def bool(self):
        s = self.string()
        if s == "1" or s.lower() == "true":
            return True
        elif s == "0" or s.lower() == "false":
            return False
        raise MSGarbageError("Invalid bool: %r" % s)

    def unpack(self, codes):
        return [ self._CODES2FUNC[c](self) for c in codes ]

    _CODES2FUNC = {
        "i": int,
        "s": string,
        "b": bool,
    }


def make_packet(*args):
    pstr = ''.join(str(x) + '\x00' for x in args)
    size = len(pstr) + 2
    return chr(size >> 8) + chr(size & 0xff) + pstr



