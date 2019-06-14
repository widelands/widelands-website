#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: tests/test_models.py
#
# Created by Holger Rapp on 2009-04-10.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

from django.conf import settings
from django.test import TestCase as DjangoTest
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from io import StringIO

from unittest import TestCase

from wlscreens.models import *


class TestCategoryAdding(DjangoTest):

    def test_addCategory_exceptCorrectResult(self):
        c = Category.objects.create(name='A new Revision')
        self.assertEqual(c.pk, 1)
        self.assertEqual(c.slug, 'a-new-revision')


class TestCategory(DjangoTest):
    urls = 'wlscreens.test_urls'

    def test_addCategoryWhichExists_exceptFail(self):
        Category.objects.create(name='A new Revision').save()
        self.assertRaises(IntegrityError,
                          Category.objects.create, name='A NEW Revision')

    def test_CategoryRepr_exceptCorrectResult(self):
        c = Category.objects.create(name='A new Revision')
        self.assertEqual(repr(c), '<Category: A new Revision>')

    def test_UrlGeneration_exceptCorrectResult(self):
        c = Category.objects.create(name='build 13')
        self.assertEqual(c.get_absolute_url(), '/wlscreens/build-13/')


class _ScreenshotBase(DjangoTest):
    urls = 'wlscreens.test_urls'

    @staticmethod
    def _make_random_image(size):
        img = Image.new('RGB', size)
        png = StringIO()
        img.save(png, 'png')
        png.seek(0)
        return SimpleUploadedFile('test.png', png.read())

    def setUp(self):
        self.c = Category.objects.create(name='build 13')
        self.c2 = Category.objects.create(name='build 14')

        self.img = _ScreenshotBase._make_random_image((640, 480))


class TestScreenshotAdding(_ScreenshotBase):

    def test_AddImage_ExpectCorrectResult(self):
        i = Screenshot.objects.create(name='First Test',
                                      category=self.c,
                                      screenshot=self.img,
                                      comment='This rockz!')
        self.assertEqual(i.pk, 1)
        self.assertEqual(i.thumbnail.width, settings.THUMBNAIL_SIZE[0])


class TestScreenshot(_ScreenshotBase):

    def setUp(self):
        _ScreenshotBase.setUp(self)

        img = _ScreenshotBase._make_random_image((6, 4))

        self.i = Screenshot.objects.create(name='First Test',
                                           category=self.c,
                                           screenshot=img,
                                           comment='This rockz!')

    def testAdd_SameNameSameCat_ExceptRaise(self):
        self.assertRaises(IntegrityError,
                          Screenshot.objects.create, name='First Test',
                          category=self.c,
                          screenshot=self.img,
                          comment='This is nice!')

    def testAdd_SameNameOtherCat_ExceptCorrectResult(self):
        k = Screenshot.objects.create(name='First Test',
                                      category=self.c2,
                                      screenshot=self.img,
                                      comment='This is nice!')

    def test_Repr_ExceptCorrectResult(self):
        self.assertEqual(repr(self.i), '<Screenshot: build 13:First Test>')

    def test_CategoryScreenshots_ExceptCorrectResult(self):
        c = self.c.screenshots.all()
        c2 = self.c2.screenshots.all()
        self.assertTrue(self.i in c)
        self.assertEqual(c.count(), 1)
        self.assertEqual(c2.count(), 0)
