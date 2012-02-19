#!/usr/bin/env python
# encoding: utf-8

from twisted.internet.protocol import Factory

from protocol import MSProtocol

__all__ = ["MetaServer"]

class MetaServer(Factory):
    def __init__(self, db):
        self.users = {}
        self.games = {}
        self.users_wanting_to_relogin = {}
        self.db = db
        self.motd = ""

    def buildProtocol(self, addr):
        return MSProtocol(self)

    def broadcast(self, *args):
        """Send a message to all connected clients"""
        for con in self.users.values():
            if not con.active:
                continue
            con.send(*args)

