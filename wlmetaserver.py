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
#
# TODO: peter fragen warum das integers sind
# TODO: peter neue replys:
    # ERROR NO_SUCH_USER username

# TODO: coole idee GAME_NOT_CONNECTABLE

INTERNET_CLIENT_UNREGISTERED = "UNREGISTERED"
INTERNET_CLIENT_REGISTERED   = "REGISTERED"
INTERNET_CLIENT_SUPERUSER    = "SUPERUSER"
INTERNET_CLIENT_BOT          = "BOT"

# import os
# os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
# import sys
# sys.path.append("..")
# from django.contrib.auth.models import User
# from wlggz.models import GGZAuth

# TODO: peek is not used
def _string(l, peek = False):
    if l:
        return l.pop(0) if not peek else l[0]
    return ''
def _int(l, *args, **kwargs):
    s = _string(l, *args, **kwargs)
    try:
        return int(s)
    except ValueError:
        return 0
def _bool(l, *args, **kwargs):
    s = _string(l, *args, **kwargs)
    if s == "1" or s.lower() == "true":
        return True
    return False

def make_packet(*args):
    pstr = ''.join(str(x) + '\x00' for x in args)
    size = len(pstr) + 2
    print "size: %r" % (size)
    print "Sending: %r" % (args,)
    return chr(size >> 8) + chr(size & 0xff) + pstr


class MSConnection(Protocol):
    _ALLOWED_PACKAGES = {
        "HANDSHAKE": set(("LOGIN","DISCONNECT")),
        "LOBBY": set(("DISCONNECT", "CHAT", "CLIENTS")),
    }

    _GGZPERMS2PERMS = {
          7: INTERNET_CLIENT_REGISTERED,
        127: INTERNET_CLIENT_SUPERUSER,
    }
    def __init__(self, factory):
        self._login_time = time.time()
        self._factory = factory
        self._name = None
        self._state = "HANDSHAKE"

        self._expect_data = 0
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
                print "Received: %r" % (packet)
                cmd = _string(packet)
                print "packet: %r" % (packet)
                if cmd in self._ALLOWED_PACKAGES[self._state]:
                    func = getattr(self, "_handle_%s" % cmd)
                    func(packet)
                else: # Garbage sended? Kick this one
                    # TODO: explain why and write test
                    self.transport.loseConnection()
                    return

    def send(self, *args):
        self.transport.write(make_packet(*args))

    def _handle_LOGIN(self, p):
        print "p: %r" % (p,)
        self._protocol_version = _int(p)
        name = _string(p)
        self._build_id = _string(p)
        if _bool(p): # Is a user with a login?
            self._name = name
            rv = self._factory.db.check_user(self._name, _string(p))
            if rv is False:
                self.send("ERROR", "LOGIN" ,"WRONG_PASSWORD")
                self.transport.loseConnection()
                return
            self._permissions = rv
        else:
            # Find a name that is not yet in use : TODO: in a function of its own
            self._name = name
            n = 1
            while self._name in self._factory.users:
                print "self._factory.users: %r" % (self._factory.users)
                self._name = name + str(n)
                n += 1
            self._permissions = INTERNET_CLIENT_UNREGISTERED

        self.send("LOGIN", self._name, self._permissions)
        self._state = "LOBBY"
        self.send("TIME", int(time.time()))

        # TODO: Peter wg lexical cast: http://www.boost.org/doc/libs/1_40_0/libs/conversion/lexical_cast.htm
        # TODO: find out what the state of this user is

        self._login_time = time.time()
        self._factory.connected(self)

    def _handle_CLIENTS(self, p):
        args = ["CLIENTS", len(self._factory.users)]
        for u in self._factory.users.values():
            # TODO: send game in third place
            # TODO: Peter: points?
            args.extend((u._name, u._build_id, '', self._permissions, "nopoints"))
        self.send(*args)
    def _handle_CHAT(self, p):
        msg = _string(p)
        receipient = _string(p)
        if not receipient: # Public Message
            self._factory.broadcast("CHAT", self._name, msg, "false", "false")
        else:
            if receipient in self._factory.users:
                self._factory.users[receipient].send("CHAT", self._name, msg, "true", "false")
            else:
                self.send("ERROR", "CHAT", "NO_SUCH_USER", receipient)
    def _handle_DISCONNECT(self, p):
        reason = _string(p)  # TODO: do somethinwith the reason
        self._factory.disconnected(self)



class MetaServer(Factory):
    def __init__(self, db):
        self.users = {}
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
