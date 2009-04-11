#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.test import TestCase as DjangoTest, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from wlscreens.models import *

import os

###########
# Helpers #
###########
class _LoginToSite(DjangoTest):
    def setUp(self):
        u = User.objects.create(username="root", email="root@root.com")
        u.set_password("root")
        u.save()
        
        self.client.login( username="root", password="root")

#############
# TestCases #
#############
###########
# Uploads #
###########
class TestWLScreens_IndexSite_ExceptCorrectResult(_LoginToSite):
    def runTest(self):
        url = reverse('wlscreens_index')
        k = self.client.get(url)

        self.assertTemplateUsed(k,"wlscreens/index.html")
        self.assertTrue("categories" in k.context)


