#!/usr/bin/python -tt

#!/usr/bin/env python -tt
# encoding: utf-8
#
# File: utests/test_wl_markdown.py
#
# Created by Holger Rapp on 2009-02-28.
# Copyright (c) 2009 HolgerRapp@gmx.net. All rights reserved.
#
# Last Modified: $Date$
#

# Since we want to include something from one path up,
# we append the parent path to sys.path
import sys

sys.path.append("..")

import PIL
from io import BytesIO

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client

from .models import Image
from .forms import UploadImageForm


class _TestUploadingBase(TestCase):
    @staticmethod
    def _make_new_uploaded_image(name, type="bmp"):
        sio = BytesIO()
        i = PIL.Image.new("RGB", (4, 4))

        i.save(sio, type)

        return SimpleUploadedFile(name, sio.read(), content_type="image/%s" % type)

    def setUp(self):
        # We need some dummy objects
        # User
        self.u = User.objects.create(username="paul")
        # A Content type
        self.ct = ContentType.objects.create(app_label="test", model="TestModel")

        self.t1 = self._make_new_uploaded_image("test.png")
        self.t2 = self._make_new_uploaded_image("test.png")
        self.o1 = self._make_new_uploaded_image("othername.png")

        self.c = Client()


###########################################################################
#                  MODEL TESTS (need database, are slow)                  #
###########################################################################
class TestImages_TestModelAdding_ExceptCorrectResult(_TestUploadingBase):
    def runTest(self):
        self.assertFalse(Image.objects.has_image("test"))
        u = Image.objects.create(
            user=self.u, content_type=self.ct, object_id=1, name="test", revision=1
        )
        self.assertEqual(Image.objects.get(name="test", revision=1), u)
        self.assertTrue(Image.objects.has_image("test"))


class TestImages_TestModelAddingTwiceTheSameNameAndRevision_ExceptRaises(
    _TestUploadingBase
):
    def runTest(self):
        u = Image.objects.create(
            user=self.u, content_type=self.ct, object_id=1, name="test", revision=1
        )
        self.assertRaises(
            Image.AlreadyExisting,
            Image.objects.create,
            **{
                "user": self.u,
                "content_type": self.ct,
                "object_id": 1,
                "name": "test",
                "revision": 1,
            },
        )


class TestImages_TestModelAddingTwiceTheSameNameDifferentRevision_ExceptRaises(
    _TestUploadingBase
):
    def runTest(self):
        u = Image.objects.create(
            user=self.u, content_type=self.ct, object_id=1, name="test", revision=1
        )
        u = Image.objects.create(
            user=self.u, content_type=self.ct, object_id=1, name="test", revision=2
        )
        self.assertEqual(Image.objects.filter(name="test").count(), 2)


###############
# Other Tests #
###############
# This test is not of much use
# class TestImages_TestUploadForm_ExceptCorrectResult(_TestUploadingBase):
#     def runTest(self):
#         form = UploadImageForm()
#         self.assertEqual( form.is_valid(), False )

if __name__ == "__main__":
    unittest.main()
    # k = TestWlMarkdown_WikiWordsInLink_ExceptCorrectResult()
    # unittest.TextTestRunner().run(k)
