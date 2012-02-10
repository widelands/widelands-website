#!/usr/bin/env python
# encoding: utf-8

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

import base64
import hashlib

import time

from wlms.db.flatfile import FlatFileDatabase

# TODO: PING regularly when no data came around
# TODO: logging
# TODO: GAME_START / GAME_END

# TODO: check chat messages for richtext tags and deny them if they include them. Only systemmessages like
#       the motd may contain them.

class MSError(Exception):
    def __init__(self, *args):
        self.args = args
class MSCriticalError(MSError):
    def __init__(self, *args):
        self.args = args
class MSGarbageError(MSCriticalError):
    def __init__(self, *args):
        MSCriticalError.__init__(self, "GARBAGE_RECEIVED", *args)

def _string(l):
    try:
        return l.pop(0)
    except IndexError:
        raise MSGarbageError("Wanted a string but got no arguments left")

def _int(l):
    s = _string(l)
    try:
        return int(s)
    except ValueError:
        raise MSGarbageError("Invalid integer: %r" % s)

def _bool(l):
    s = _string(l)
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

class Game(object):
    __slots__ = ("host", "max_players", "name", "buildid", "players", "_opening_time")

    def __init__(self, host, name, max_players, buildid):
        """
        Representing a currently running game.

        :host: The name of the hosting player
        :max_players: Number of players the game can hold
        :players: a set of the player names currently in the game.
            Includes the host
        """
        self.host = host
        self.max_players = max_players
        self.players = set((host,))
        self.name = name
        self.buildid = buildid

        self._opening_time = time.time()

    def __lt__(self, o):
        return self._opening_time < o._opening_time

    @property
    def connectable(self): # TODO check connectability
        return not self.full

    @property
    def full(self):
        return len(self.players) >= self.max_players


class MSConnection(Protocol):
    _ALLOWED_PACKAGES = {
        "HANDSHAKE": set(("LOGIN","DISCONNECT", "RELOGIN")),
        "LOBBY": set((
            "DISCONNECT", "CHAT", "CLIENTS", "RELOGIN", "PONG", "GAME_OPEN",
            "GAME_CONNECT", "GAMES", "MOTD",
        )),
        "INGAME": set((
            "DISCONNECT", "CHAT", "CLIENTS", "RELOGIN", "PONG", "GAMES",
            "GAME_DISCONNECT", "MOTD",
        )),
    }
    callLater = reactor.callLater

    def __init__(self, ms):
        self._login_time = time.time()
        self._ms = ms
        self._name = None
        self._state = "HANDSHAKE"
        self._game = ""

        self._d = ""

    def __lt__(self, o):
        return self._login_time < o._login_time

    def connectionLost(self, reason):
        self._ms.disconnected(self)

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

        while True:
            packet = self._read_packet()
            if packet is None:
                break

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
                    raise MSGarbageError("INVALID_CMD")
            except MSCriticalError as e:
                self.send("ERROR", *e.args)
                self.transport.loseConnection()
                return
            except MSError as e:
                self.send("ERROR", *e.args)


    def send(self, *args):
        self.transport.write(make_packet(*args))

    def _handle_LOGIN(self, p, cmdname = "LOGIN"):
        self._protocol_version, name, self._buildid, is_registered = _unpack("issb", p)

        if self._protocol_version != 0:
            raise MSCriticalError("UNSUPPORTED_PROTOCOL")

        if is_registered:
            rv = self._ms.db.check_user(name, _string(p))
            if rv is False:
                raise MSError("WRONG_PASSWORD")
            if name in self._ms.users:
                raise MSError("ALREADY_LOGGED_IN")
            self._name = name
            self._permissions = rv
        else:
            # Find a name that is not yet in use
            temp = name
            n = 1
            while temp in self._ms.users or self._ms.db.user_exists(temp):
                temp = name + str(n)
                n += 1
            self._name = temp
            self._permissions = "UNREGISTERED"

        self.send("LOGIN", self._name, self._permissions)
        self._state = "LOBBY"
        self._login_time = time.time()
        self.send("TIME", int(time.time()))
        self._ms.connected(self)

        if self._ms.motd:
            self.send("CHAT", '', self._ms.motd, "false", "true")


    def _handle_MOTD(self, p):
        motd = _string(p)
        if self._permissions != "SUPERUSER":
            raise MSError("DEFICIENT_PERMISSION")
        self._ms.motd = motd
        self._ms.broadcast("CHAT", '', self._ms.motd, "false", "true")


    def _handle_PONG(self, p):
        if self._name in self._ms.users_wanting_to_relogin:
            # No, you can't relogin. Sorry
            pself, new, defered = self._ms.users_wanting_to_relogin.pop(self._name)
            assert(pself is self)
            new.send("ERROR", "RELOGIN", "CONNECTION_STILL_ALIVE")
            defered.cancel()

    def _handle_RELOGIN(self, p):
        pv, name, build_id, is_registered = _unpack("issb", p)
        if name not in self._ms.users:
            raise MSError("NOT_LOGGED_IN")

        u = self._ms.users[name]
        if (u._protocol_version != pv or u._buildid != build_id):
            raise MSError("WRONG_INFORMATION")
        if (is_registered and u._permissions == "UNREGISTERED" or
            (not is_registered and u._permissions == "REGISTERED")):
            raise MSError("WRONG_INFORMATION")

        if is_registered and not self._ms.db.check_user(name, _string(p)):
            raise MSError("WRONG_INFORMATION")

        u.send("PING")

        def _try_relogin():
            del self._ms.users_wanting_to_relogin[u._name]
            u.send("DISCONNECT", "TIMEOUT")
            u.transport.loseConnection()
            self._ms.users[self._name] = self
            self.send("RELOGIN")
        defered = self.callLater(5, _try_relogin)
        self._ms.users_wanting_to_relogin[u._name] = (u, self, defered)

    def _handle_CLIENTS(self, p):
        args = ["CLIENTS", len(self._ms.users)]
        for u in sorted(self._ms.users.values()):
            args.extend((u._name, u._buildid, u._game, u._permissions, ''))
        self.send(*args)

    def _handle_CHAT(self, p):
        msg, recipient = _unpack("ss", p)
        if not recipient: # Public Message
            self._ms.broadcast("CHAT", self._name, msg, "false", "false")
        else:
            if recipient in self._ms.users:
                self._ms.users[recipient].send("CHAT", self._name, msg, "true", "false")
            else:
                self.send("ERROR", "CHAT", "NO_SUCH_USER", recipient)

    def _handle_GAME_OPEN(self, p):
        name, max_players = _unpack("si", p)

        if name in self._ms.games:
            raise MSError("GAME_EXISTS")

        game = Game(self._name, name, max_players, self._buildid)
        self._ms.games[name] = game
        self._ms.broadcast("GAMES_UPDATE")

        self._game = name
        self._state = "INGAME"
        self._ms.broadcast("CLIENTS_UPDATE")

        self.send("GAME_OPEN")

    def _handle_GAMES(self, p):
        args = ["GAMES", len(self._ms.games)]
        for game in sorted(self._ms.games.values()):
            con = "true" if game.connectable else "false"
            args.extend((game.name, game.buildid, con))
        self.send(*args)

    def _handle_GAME_CONNECT(self, p):
        name, = _unpack("s", p)

        if name not in self._ms.games:
            raise MSError("NO_SUCH_GAME")
        game = self._ms.games[name]
        if game.host not in self._ms.users:
            raise MSError("INVALID_HOST")
        if game.full:
            raise MSError("GAME_FULL")

        self.send("GAME_CONNECT", self._ms.users[game.host].transport.client[0])
        game.players.add(self._name)

        self._game = game.name
        self._state = "INGAME"
        self._ms.broadcast("CLIENTS_UPDATE")

    def _handle_GAME_DISCONNECT(self, p):
        game = self._game
        send_games_update = False
        if self._game in self._ms.games:
            game = self._ms.games[self._game]

            game.players.remove(self._name)
            if game.host == self._name:
                del self._ms.games[game.name]
                send_games_update = True

        self._game = ""
        self.send("GAME_DISCONNECT")
        self._state = "LOBBY"
        self._ms.broadcast("CLIENTS_UPDATE")
        if send_games_update:
            self._ms.broadcast("GAMES_UPDATE")

    def _handle_DISCONNECT(self, p):
        reason = _string(p)  # TODO: do somethinwith the reason
        self.transport.loseConnection()
        self._ms.disconnected(self)



class MetaServer(Factory):
    def __init__(self, db):
        self.users = {}
        self.games = {}
        self.users_wanting_to_relogin = {}
        self.db = db
        self.motd = ""

    def buildProtocol(self, addr):
        return MSConnection(self)


    def disconnected(self, con):
        if con._name in self.users:
            del self.users[con._name]
        self.broadcast("CLIENTS_UPDATE")

    def connected(self, con):
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
