#!/usr/bin/env python
# encoding: utf-8

from collections import namedtuple

class FlatFileDatabase(object):
    def __init__(self, text):
        """
        A database that can be read from a flat file. Mainly for testing. text
        is the complete text inside the definition file.
        """
        self._users = {}
        for line in text.splitlines():
            line = line.strip()
            if not line: continue
            elems = line.split("\t")
            self._users[elems[0]] = elems[1], elems[2]

    def check_user(self, user, password):
        if not user in self._users:
            return False
        u = self._users[user]
        if u[0] == password:
            return u[1]
        return False

    def user_exists(self, user):
        return user in self._users

