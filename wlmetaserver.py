#!/usr/bin/env python
# encoding: utf-8

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

import base64
import hashlib

import time

from wlms.db.flatfile import FlatFileDatabase

# TODO: relogin
# TODO: MOTD
# TODO: PING, PONG
# TODO: GAME STUFF

# TODO: check chat messages for richtext tags and deny them if they include them. Only systemmessages like
#       the motd may contain them.

# import os
# os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
# import sys
# sys.path.append("..")
# from django.contrib.auth.models import User
# from wlggz.models import GGZAuth

class MSError(Exception):
    def __init__(self, *args):
        self.args = args
class MSCriticalError(Exception):
    def __init__(self, *args):
        self.args = args
class MSGarbageError(MSCriticalError):
    def __init__(self, *args):
        MSCriticalError.__init__(self, "GARBAGE_RECEIVED", *args)

# TODO: peek is not used
def _string(l, peek = False):
    if l:
        return l.pop(0) if not peek else l[0]
    raise MSGarbageError("Wanted a string but got no arguments left")

def _int(l, *args, **kwargs):
    s = _string(l, *args, **kwargs)
    try:
        return int(s)
    except ValueError:
        raise MSGarbageError("Invalid integer: %r" % s)

def _bool(l, *args, **kwargs):
    s = _string(l, *args, **kwargs)
    if s == "1" or s.lower() == "true":
        return True
    elif s == "0" or s.lower() == "false":
        return False
    raise MSGarbageError("Invalid bool: %r" % s)

__CODES2FUNC = {
    "i": _int,
    "s": _string,
    "b": _bool,
}
def _unpack(codes, p):
    return [ __CODES2FUNC[c](p) for c in codes ]

def make_packet(*args):
    pstr = ''.join(str(x) + '\x00' for x in args)
    size = len(pstr) + 2
    return chr(size >> 8) + chr(size & 0xff) + pstr

class MSConnection(Protocol):
    _ALLOWED_PACKAGES = {
        "HANDSHAKE": set(("LOGIN","DISCONNECT", "RELOGIN")),
        "LOBBY": set(("DISCONNECT", "CHAT", "CLIENTS", "RELOGIN", "PONG")),
    }
    callLater = reactor.callLater

    def __init__(self, factory):
        self._login_time = time.time()
        self._factory = factory
        self._name = None
        self._state = "HANDSHAKE"
        self._last_pong = self._login_time

        self._d = ""

    def __lt__(self, o):
        return self._login_time < o._login_time

    def connectionLost(self, reason):
        self._factory.disconnected(self)

    def _read_packet(self):
        if len(self._d) < 2: # Length there?
            return

        size = (ord(self._d[0]) << 8) + ord(self._d[1])
        if len(self._d) < size: # All of packet there?
            return

        packet_data = self._d[2:2+(size-2)]
        self._d = self._d[size:]

        return packet_data[:-1].split('\x00')

    def dataReceived(self, data):
        self._d += data

        packet = 1
        while packet:
            packet = self._read_packet()

            if packet is not None:
                try:
                    cmd = _string(packet)
                    if cmd in self._ALLOWED_PACKAGES[self._state]:
                        func = getattr(self, "_handle_%s" % cmd)
                        try:
                            func(packet)
                        except MSGarbageError as e:
                            e.args = (cmd,) + e.args[1:]
                            raise e
                        except MSError as e:
                            e.args = (cmd,) + e.args
                            raise e
                    else:
                        raise MSGarbageError("Invalid or forbidden command: '%s'" % cmd)
                except MSCriticalError as e:
                    self.send("ERROR", *e.args)
                    self.transport.loseConnection()
                    return
                except MSError as e:
                    self.send("ERROR", *e.args)


    def send(self, *args):
        self.transport.write(make_packet(*args))

    def _handle_LOGIN(self, p, cmdname = "LOGIN"):
        self._protocol_version, name, self._build_id, is_registered = _unpack("issb", p)
        if is_registered:
            rv = self._factory.db.check_user(name, _string(p))
            if rv is False:
                raise MSError("WRONG_PASSWORD")
            if name in self._factory.users:
                raise MSError("ALREADY_LOGGED_IN")
            self._name = name
            self._permissions = rv
        else:
            # Find a name that is not yet in use
            temp = name
            n = 1
            while temp in self._factory.users or self._factory.db.user_exists(temp):
                temp = name + str(n)
                n += 1
            self._name = temp
            self._permissions = "UNREGISTERED"

        self.send("LOGIN", self._name, self._permissions)
        self._state = "LOBBY"
        self._login_time = time.time()
        self.send("TIME", int(time.time()))

        self._factory.connected(self)

    def _handle_PONG(self, p):
        self._last_pong = time.time()

        if self._name in self._factory.users_wanting_to_relogin:
            # No, you can't relogin. Sorry
            pself, new, defered = self._factory.users_wanting_to_relogin.pop(self._name)
            assert(pself is self)
            new.send("ERROR", "RELOGIN", "CONNECTION_STILL_ALIVE")
            defered.cancel()

    def _handle_RELOGIN(self, p):
        pv, name, build_id, is_registered = _unpack("issb", p)
        if name not in self._factory.users:
            raise MSError("NOT_LOGGED_IN")

        u = self._factory.users[name]
        if (u._protocol_version != pv or u._build_id != build_id):
            raise MSError("WRONG_INFORMATION")
        if (is_registered and u._permissions == "UNREGISTERED" or
            (not is_registered and u._permissions == "REGISTERED")):
            raise MSError("WRONG_INFORMATION")

        if is_registered and not self._factory.db.check_user(name, _string(p)):
            raise MSError("WRONG_INFORMATION")

        u.send("PING")

        def _try_relogin():
            del self._factory.users_wanting_to_relogin[u._name]
            u.send("DISCONNECT", "TIMEOUT")
            u.transport.loseConnection()
            self._factory.users[self._name] = self
            self.send("RELOGIN")
        defered = self.callLater(5, _try_relogin)
        self._factory.users_wanting_to_relogin[u._name] = (u, self, defered)

    def _handle_CLIENTS(self, p):
        args = ["CLIENTS", len(self._factory.users)]
        for u in sorted(self._factory.users.values()):
            # TODO: send game in third place
            args.extend((u._name, u._build_id, '', u._permissions, ''))
        self.send(*args)

    def _handle_CHAT(self, p):
        msg, recipient = _unpack("ss", p)
        if not recipient: # Public Message
            self._factory.broadcast("CHAT", self._name, msg, "false", "false") # TODO: warum zwei flags?
        else:
            if recipient in self._factory.users:
                self._factory.users[recipient].send("CHAT", self._name, msg, "true", "false")
            else:
                self.send("ERROR", "CHAT", "NO_SUCH_USER", recipient)

    def _handle_DISCONNECT(self, p):
        reason = _string(p)  # TODO: do somethinwith the reason
        self.transport.loseConnection()
        self._factory.disconnected(self)



class MetaServer(Factory):
    def __init__(self, db):
        self.users = {}
        self.users_wanting_to_relogin = {}
        self.db = db

    def buildProtocol(self, addr):
        return MSConnection(self)

    def disconnected(self, con):
        if con._name in self.users:
            del self.users[con._name]
        self.broadcast("CLIENTS_UPDATE")

    def connected(self, con):
        print "Has connected: con._name: %r" % (con._name)
        self.users[con._name] = con
        self.broadcast("CLIENTS_UPDATE")

    def broadcast(self, *args):
        """Send a message to all connected clients"""
        for con in self.users.values():
            con.send(*args)

from optparse import OptionParser

def parse_args():
    parser = OptionParser()
    parser.add_option("-d", "--dbfile", default="",
        help="Use flatfile database. File format is 'user\\tpassword\\tpermissions\n'", metavar="DB")
    parser.add_option("-p", "--port", type=int, default=7395,
        help="Listen on this port")

    return parser.parse_args()

def main():
    o, args = parse_args()

    if not o.dbfile:
        raise RuntimeError("Need a flat file as database for the moment!")
    db = FlatFileDatabase(open(o.dbfile, "r").read())

    reactor.listenTCP(o.port, MetaServer(db))
    reactor.run()

if __name__ == '__main__':
    main()
