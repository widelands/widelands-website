#!/usr/bin/env python
# encoding: utf-8

import logging
import re

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import Protocol, ClientFactory

from wlms.errors import MSCriticalError, MSError, MSGarbageError
from wlms.utils import make_packet, Packet

class Game(object):
    __slots__ = ("host", "max_players", "name", "buildid", "players", "_opening_time", "state")

    def __init__(self, opening_time, host, name, max_players, buildid):
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

        self.state = "ping_pending"
        self._opening_time = opening_time

    def __lt__(self, o):
        return self._opening_time < o._opening_time

    def start(self):
        self.state = "running"

    @property
    def connectable(self):
        if self.state != "accepting_connections":
            return False
        return not self.full

    @property
    def full(self):
        return len(self.players) >= self.max_players

import time
NETCMD_METASERVER_PING = "\x00\x03@"
class GamePing(Protocol):

    def __init__(self, fac, client_protocol, timeout):
        self._client_protocol = client_protocol
        self._noreplycall = self._client_protocol.callLater(
            timeout, fac.no_reply
        )
        self._fac = fac

    def connectionMade(self):
        self.transport.write(NETCMD_METASERVER_PING)

    def dataReceived(self, data):
        self._noreplycall.cancel()
        if data != NETCMD_METASERVER_PING:
            self._fac.no_reply()
            return

        game = self._client_protocol._ms.games.get(self._client_protocol._game, None)
        # This could be a game ping for a game that has been ended and a new
        # one has already started. If we know nothing about the game, ignore
        # this silently.
        if game is None:
            return

        if game.state == "ping_pending": # Game is valid. Let's go
            game.state = "accepting_connections"
            self._client_protocol.send("GAME_OPEN")
            self._client_protocol._ms.broadcast("GAMES_UPDATE")
            logging.info("Game Pong for %s received. Game is connectable!", game.name)

        self._client_protocol.callLater(
            self._client_protocol.GAME_PING_PAUSE,
            self._client_protocol.create_game_pinger,
            self._client_protocol,
            self._client_protocol.GAME_PING_PAUSE,
        )

class GamePingFactory(ClientFactory):
    def __init__(self, client_protocol, timeout):
        self._client_protocol = client_protocol
        self._timeout = timeout

    def no_reply(self):
        game = self._client_protocol._ms.games[self._client_protocol._game]
        if game.state == "ping_pending": # Game is valid. Let's go
            self._client_protocol.send("ERROR", "GAME_OPEN", "GAME_TIMEOUT")
            logging.info("Game Pong for %s not received. Game is unreachable after opening!", game.name)
            game.state = "unreachable"
        else:
            logging.info("Game Pong for %s not received. Game is no longer reachable, so we assume it is over.", game.name)
            del self._client_protocol._ms.games[game.name]
        self._client_protocol._ms.broadcast("GAMES_UPDATE")

    def clientConnectionFailed(self, connector, reason):
        self.no_reply()

    def buildProtocol(self, addr):
        return GamePing(self, self._client_protocol, self._timeout)

def _create_game_pinger(pc, timeout):
    reactor.connectTCP(pc.transport.client[0], 7396, GamePingFactory(pc, timeout), pc.GAME_PING_TIME_FOR_FIRST_REPLY)

class MSProtocol(Protocol):
    _ALLOWED_PACKAGES = {
        "handshake": set(("LOGIN","DISCONNECT", "RELOGIN")),
        "lobby": set((
            "DISCONNECT", "CHAT", "CLIENTS", "RELOGIN", "PONG", "GAME_OPEN",
            "GAME_CONNECT", "GAMES", "MOTD", "ANNOUNCEMENT",
        )),
        "ingame": set((
            "DISCONNECT", "CHAT", "CLIENTS", "RELOGIN", "PONG", "GAMES",
            "GAME_DISCONNECT", "MOTD", "ANNOUNCEMENT", "GAME_START"
        )),
    }
    REMEMBER_CLIENT_FOR = 60*5
    PING_WHEN_SILENT_FOR = 10
    GAME_PING_TIME_FOR_FIRST_REPLY = 5
    GAME_PING_PAUSE = 120
    callLater = reactor.callLater
    seconds = reactor.seconds
    create_game_pinger = staticmethod(_create_game_pinger)

    def __init__(self, ms):
        self._login_time = self.seconds()
        self._pinger = None
        self._cleaner = None
        self._have_sended_ping = False
        self._ms = ms
        self._name = None
        self._state = "handshake"
        self._recently_disconnected = False
        self._game = ""
        self._buildid = None
        self._permissions = None

        self._d = ""

    def _copy_attr(self, o):
        self._login_time = o._login_time
        self._ms = o._ms
        self._name = o._name
        self._state = o._state
        self._game = o._game
        self._buildid = o._buildid
        self._permissions = o._permissions


    def __lt__(self, o):
        return self._login_time < o._login_time

    def connectionLost(self, reason):
        logging.info("%r disconnected: %s", self._name, reason.getErrorMessage())
        if self._pinger:
            self._pinger.cancel()
            self._pinger = None
        self._cleaner = self.callLater(self.REMEMBER_CLIENT_FOR, self._forget_me)
        self._recently_disconnected = True
        self._ms.broadcast("CLIENTS_UPDATE")

    def dataReceived(self, data):
        self._d += data

        if self._pinger:
            self._pinger.reset(self.PING_WHEN_SILENT_FOR)
            self._have_sended_ping = False

        while True:
            packet = self._read_packet()
            if packet is None:
                break
            logging.debug("Packet from %s: %s", self._name, packet)
            packet = Packet(packet)

            try:
                cmd = packet.string()
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
                logging.warning("Terminating connection to %r: %s", self._name, e.args)
                self.transport.loseConnection()
                return
            except MSError as e:
                self.send("ERROR", *e.args)

    def send(self, *args):
        self.transport.write(make_packet(*args))

    # Private Functions {{{
    def _read_packet(self):
        if len(self._d) < 2: # Length there?
            return

        size = (ord(self._d[0]) << 8) + ord(self._d[1])
        if len(self._d) < size: # All of packet there?
            return

        packet_data = self._d[2:2+(size-2)]
        self._d = self._d[size:]

        return packet_data[:-1].split('\x00')

    def _ping_or_disconnect(self):
        if not self._have_sended_ping:
            self.send("PING")
            self._have_sended_ping = True
        else:
            self.send("DISCONNECT", "CLIENT_TIMEOUT")
            self.transport.loseConnection()
        self._pinger = self.callLater(self.PING_WHEN_SILENT_FOR, self._ping_or_disconnect)

    def _forget_me(self): # We have been disconnected for a long time, finally forget me
        if self._cleaner:
            self._cleaner.cancel()
        del self._ms.users[self._name]

    def _handle_LOGIN(self, p, cmdname = "LOGIN"):
        self._protocol_version, name, self._buildid, is_registered = p.unpack("issb")

        if self._protocol_version != 0:
            raise MSCriticalError("UNSUPPORTED_PROTOCOL")

        if is_registered:
            rv = self._ms.db.check_user(name, p.string())
            if rv is False:
                raise MSError("WRONG_PASSWORD")
            if name in self._ms.users:
                ou = self._ms.users[name]
                if ou._recently_disconnected:
                    ou._forget_me()
                else:
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
        self._state = "lobby"
        self._login_time = self.seconds()
        self._pinger = self.callLater(self.PING_WHEN_SILENT_FOR, self._ping_or_disconnect)

        self.send("TIME", int(self.seconds()))

        logging.info("%r has logged in as %s", self._name, self._permissions)
        self._ms.users[self._name] = self
        self._ms.broadcast("CLIENTS_UPDATE")

        if self._ms.motd:
            self.send("CHAT", '', self._ms.motd, "system")


    def _handle_MOTD(self, p):
        motd = p.string()
        if self._permissions != "SUPERUSER":
            logging.warning("%r tried setting MOTD with permission %s. Denied.", self._name, self._permissions)
            raise MSError("DEFICIENT_PERMISSION")
        self._ms.motd = motd
        self._ms.broadcast("CHAT", '', self._ms.motd, "system")

    def _handle_ANNOUNCEMENT(self, p):
        msg = p.string()
        if self._permissions != "SUPERUSER":
            logging.warning("%r tried to send an announcement with permission %s. Denied.", self._name, self._permissions)
            raise MSError("DEFICIENT_PERMISSION")
        self._ms.broadcast("CHAT", '', msg, "system")


    def _handle_PONG(self, p):
        if self._name in self._ms.users_wanting_to_relogin:
            # No, you can't relogin. Sorry
            pself, new, defered = self._ms.users_wanting_to_relogin.pop(self._name)
            assert(pself is self)
            new.send("ERROR", "RELOGIN", "CONNECTION_STILL_ALIVE")
            defered.cancel()

    def _handle_RELOGIN(self, p):
        pv, name, build_id, is_registered = p.unpack("issb")
        if name not in self._ms.users:
            raise MSError("NOT_LOGGED_IN")

        u = self._ms.users[name]
        if (u._protocol_version != pv or u._buildid != build_id):
            raise MSError("WRONG_INFORMATION")
        if (is_registered and u._permissions == "UNREGISTERED" or
            (not is_registered and u._permissions == "REGISTERED")):
            raise MSError("WRONG_INFORMATION")

        if is_registered and not self._ms.db.check_user(name, p.string()):
            raise MSError("WRONG_INFORMATION")

        def _try_relogin():
            logging.info("User %s has not answered relogin ping. Kicking and replacing!", u._name)
            self._ms.users_wanting_to_relogin.pop(u._name, None)
            if not u._recently_disconnected:
                u.send("DISCONNECT", "CLIENT_TIMEOUT")
                u.transport.loseConnection()
            u._forget_me()
            self._copy_attr(u)
            self._ms.users[self._name] = self
            self.send("RELOGIN")

        logging.info("%s wants to relogin.", name)
        print "u._recently_disconnected: %r" % (u._recently_disconnected)
        if u._recently_disconnected:
            _try_relogin()
        else:
            u.send("PING")
            defered = self.callLater(5, _try_relogin)
            self._ms.users_wanting_to_relogin[u._name] = (u, self, defered)

    def _handle_CLIENTS(self, p):
        args = ["CLIENTS", len(self._ms.users)]
        for u in sorted(self._ms.users.values()):
            if u._recently_disconnected:
                continue
            args.extend((u._name, u._buildid, u._game, u._permissions, ''))
        self.send(*args)

    def _handle_CHAT(self, p):
        msg, recipient = p.unpack("ss")

        # Sanitize the msg: remove < and replace via '&lt;'
        msg = msg.replace("<", "&lt;")

        if not recipient: # Public Message
            self._ms.broadcast("CHAT", self._name, msg, "public")
        else:
            if recipient in self._ms.users:
                self._ms.users[recipient].send("CHAT", self._name, msg, "private")
            else:
                self.send("ERROR", "CHAT", "NO_SUCH_USER", recipient)

    def _handle_GAME_OPEN(self, p):
        name, max_players = p.unpack("si")

        if name in self._ms.games:
            raise MSError("GAME_EXISTS")

        game = Game(self.seconds(), self._name, name, max_players, self._buildid)
        self._ms.games[name] = game
        self._ms.broadcast("GAMES_UPDATE")

        self._game = name
        self._state = "ingame"
        self._ms.broadcast("CLIENTS_UPDATE")

        self.create_game_pinger(self, self.GAME_PING_TIME_FOR_FIRST_REPLY)

        logging.info("%r has opened a new game called %r. Waiting for game pong.", self._name, game.name)

    def _handle_GAMES(self, p):
        args = ["GAMES", len(self._ms.games)]
        for game in sorted(self._ms.games.values()):
            con = "true" if game.connectable else "false"
            args.extend((game.name, game.buildid, con))
        self.send(*args)

    def _handle_GAME_CONNECT(self, p):
        name, = p.unpack("s")

        if name not in self._ms.games:
            raise MSError("NO_SUCH_GAME")
        game = self._ms.games[name]
        if game.host not in self._ms.users:
            raise MSError("INVALID_HOST")
        if game.full:
            raise MSError("GAME_FULL")

        self.send("GAME_CONNECT", self._ms.users[game.host].transport.client[0])
        game.players.add(self._name)
        logging.info("%r has joined the game %r", self._name, game.name)

        self._game = game.name
        self._state = "ingame"
        self._ms.broadcast("CLIENTS_UPDATE")

    def _handle_GAME_DISCONNECT(self, p):
        send_games_update = False
        if self._game in self._ms.games:
            game = self._ms.games[self._game]

            game.players.remove(self._name)
            if game.host == self._name:
                del self._ms.games[game.name]
                send_games_update = True
            logging.info("%r has left the game %r", self._name, game.name)

        self._game = ""
        self._state = "lobby"
        self._ms.broadcast("CLIENTS_UPDATE")
        if send_games_update:
            self._ms.broadcast("GAMES_UPDATE")

    def _handle_GAME_START(self, p):
        if self._game in self._ms.games:
            game = self._ms.games[self._game]
            if game.host != self._name:
                raise MSError("DEFICIENT_PERMISSION")
                return

            game.start()
            self.send("GAME_START")
            self._ms.broadcast("GAMES_UPDATE")

    def _handle_DISCONNECT(self, p):
        reason = p.string()
        logging.info("%r left: %s", self._name, reason)
        self.transport.loseConnection()
    # End: Private Functions }}}



