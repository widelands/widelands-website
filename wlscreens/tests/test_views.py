#!/usr/bin/env python -tt
# encoding: utf-8
#

from django.test import TestCase as DjangoTest, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from wlscreens.models import *

import os

#############
# TestCases #
#############
###########
# Uploads #
###########
class TestWLScreens_IndexSite_ExceptCorrectResult(DjangoTest):
    def runTest(self):
        url = reverse('wlscreens_index')
        k = self.client.get(url)

        self.assertTemplateUsed(k,"wlscreens/index.html")
        self.assertTrue(k.context["categories"] is not None)

class TestWLScreens_CategorySite_Except404(DjangoTest):
    urls = "wlscreens.test_urls"
    def setUp(self):
        c = Category.objects.create(name="A new Revision")
    def runTest(self):
        url = reverse('wlscreens_category', None, {"category_slug": "a-new-revision"})
        c = self.client.get(url)

        self.assertEqual(c.status_code, 404 )



