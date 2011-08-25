#!/usr/bin/env python -tt
# encoding: utf-8
#
# Created by Timo Wingender <timo.wingender@gmx.de> on 2010-06-03.
#
# Last Modified: $Date$
#


# This is an auto-generated and eddited representation for the ggzd tables.
#

from django.db import models
from django.db.models import OneToOneField, ForeignKey
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

import datetime

def ggz_userlink(user):
    data = u'<a href="%s">%s</a>' % (\
        reverse('wlggz_userstats', args=[user.username]), user.username)
    return mark_safe(data)

class GGZMatches(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.IntegerField()
    game = models.TextField()
    winner = models.CharField(max_length=256)
    winner_user = ForeignKey(User, to_field='username', db_column='winner', related_name='wlggz_matchwins')
    savegame = models.TextField(blank=True)

    def winner_as_userlink(self):
        try:
            return ggz_userlink(self.winner_user)
        except:
            if len(self.winner) > 0:
                return "%s[Guest]" % (self.winner)
            return ""

    class Meta:
        db_table = u'wlggz_matches'

    def date_date(self):
        return datetime.datetime.fromtimestamp(self.date)

class GGZMatchplayers(models.Model):
    id = models.IntegerField(primary_key=True)
    match = ForeignKey(GGZMatches, to_field='id', db_column='match', related_name='wlggz_matchplayers')
    handle_user = ForeignKey(User, to_field='username', db_column='handle', related_name='wlggz_matches')
    handle = models.CharField(max_length=256)
    playertype = models.CharField(max_length=768)
    result = models.CharField(max_length=10)
    points = models.IntegerField()
    team = models.IntegerField()

    def handle_as_userlink(self):
        try:
            return ggz_userlink(self.handle_user)
        except:
            return "%s[Guest]" % (self.handle)

    class Meta:
        db_table = u'wlggz_matchplayers'

class GGZPermissions(models.Model):
    handle = models.CharField(max_length=768, blank=True)
    join_table = models.IntegerField(null=True, blank=True)
    launch_table = models.IntegerField(null=True, blank=True)
    rooms_login = models.IntegerField(null=True, blank=True)
    rooms_admin = models.IntegerField(null=True, blank=True)
    chat_announce = models.IntegerField(null=True, blank=True)
    chat_bot = models.IntegerField(null=True, blank=True)
    no_stats = models.IntegerField(null=True, blank=True)
    edit_tables = models.IntegerField(null=True, blank=True)
    table_privmsg = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'wlggz_permissions'


#class Savegameplayers(models.Model):
#    id = models.IntegerField(primary_key=True)
#    tableid = models.IntegerField()
#    stamp = models.IntegerField()
#    seat = models.IntegerField()
#    handle = models.CharField(max_length=768, blank=True)
#    seattype = models.CharField(max_length=768)
#    class Meta:
#        db_table = u'savegameplayers'

#class Savegames(models.Model):
#    id = models.IntegerField(primary_key=True)
#    date = models.IntegerField()
#    game = models.CharField(max_length=768)
#    owner = models.CharField(max_length=768)
#    savegame = models.CharField(max_length=768)
#    tableid = models.IntegerField()
#    stamp = models.IntegerField()
#    class Meta:
#        db_table = u'savegames'

class GGZStats(models.Model):
    id = models.IntegerField(primary_key=True)
    handle_user = OneToOneField(User, to_field='username', related_name='wlggzstats', db_column='handle') 
    handle = models.CharField(max_length=768, blank=True)
    game = models.TextField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    ties = models.IntegerField()
    forfeits = models.IntegerField()
    rating = models.FloatField()
    ranking = models.IntegerField()
    highscore = models.IntegerField()

    def handle_as_userlink():
        try:
            return ggz_userlink(self.handle_user)
        except:
            return "%s[Guest]" % (self.handle)

    class Meta:
        db_table = u'wlggz_stats'

#class GGZTeammembers(models.Model):
#    id = models.IntegerField(primary_key=True)
#    teamname = models.TextField()
#    username = models.TextField()
#    role = models.TextField()
#    entrydate = models.IntegerField()
#    class Meta:
#        db_table = u'ggz_db.teammembers'

#class Teams(models.Model):
#    id = models.IntegerField(primary_key=True)
#    teamname = models.TextField()
#    fullname = models.TextField()
#    icon = models.TextField()
#    foundingdate = models.IntegerField()
#    founder = models.TextField()
#    homepage = models.TextField()
#    class Meta:
#        db_table = u'ggz_db.teams'

#class Tournamentplayers(models.Model):
#    id = models.IntegerField(primary_key=True)
#    tid = models.IntegerField()
#    number = models.IntegerField()
#    name = models.TextField()
#    playertype = models.TextField()
#    class Meta:
#        db_table = u'tournamentplayers'

#class Tournaments(models.Model):
#    id = models.IntegerField(primary_key=True)
#    name = models.TextField()
#    game = models.TextField()
#    date = models.IntegerField()
#    organizer = models.TextField()
#    class Meta:
#        db_table = u'tournaments'

#class Userinfo(models.Model):
#    id = models.IntegerField(primary_key=True)
#    handle = models.CharField(max_length=768)
#    photo = models.TextField()
#    gender = models.TextField()
#    country = models.TextField()
#    pubkey = models.TextField()
#    blogfeed = models.TextField()
#    longitude = models.FloatField()
#    latitude = models.FloatField()
#    alterpass = models.TextField()
#    class Meta:
#        db_table = u'userinfo'

#class Users(models.Model):
#    id = models.IntegerField()
#    handle = models.CharField(max_length=90)
#    password = models.CharField(max_length=240, blank=True)
#    name = models.CharField(max_length=183)
#    email = models.CharField(max_length=225)
#    firstlogin = models.DateTimeField()
#    lastlogin = models.DateTimeField(null=True, blank=True)
#    permissions = models.IntegerField(null=True, blank=True)
#    confirmed = models.IntegerField(null=True, blank=True)
#    class Meta:
#        db_table = u'users'

