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

import shutil
import tempfile

import PIL
from io import BytesIO

from django.test import TestCase, override_settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client
from django.urls import reverse
from django_messages.models import Message

from wiki.models import Article

from .models import Image

# kann das weg weil weiter unter ist es auskommentiert
# from .forms import UploadImageForm


class _TestUploadingBase(TestCase):
    @staticmethod
    def _make_new_uploaded_image(name, type="bmp"):
        sio = BytesIO()
        i = PIL.Image.new("RGB", (4, 4))

        i.save(sio, type)

        return SimpleUploadedFile(name, sio.read(), content_type=f"image/{type}")

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


class TestUploadView(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media_root)
        override = override_settings(MEDIA_ROOT=self.media_root)
        override.enable()
        self.addCleanup(override.disable)

        self.user = User.objects.create_user(username="paul", password="pw")
        self.article = Article.objects.create(title="SomeArticle", content="x")
        self.article_ct = ContentType.objects.get_for_model(Article)
        self.client.force_login(self.user)

    @staticmethod
    def _png(name, color):
        sio = BytesIO()
        PIL.Image.new("RGB", (4, 4), color).save(sio, "png")
        return SimpleUploadedFile(name, sio.getvalue(), content_type="image/png")

    def _url(self, content_type, object_id, next="/wiki/edit/SomeArticle/"):
        return reverse(
            "wlimages_upload",
            kwargs={"content_type": content_type, "object_id": object_id, "next": next},
        )

    def _upload(self, name, color="red", next="/wiki/edit/SomeArticle/"):
        return self.client.post(
            self._url(self.article_ct.pk, self.article.pk, next),
            {"imagename": self._png(name, color)},
        )

    def test_non_article_object_is_not_disclosed(self):
        other = User.objects.create_user(username="other")
        message = Message.objects.create(
            subject="Secret plan", body="b", sender=other, recipient=other
        )
        url = self._url(ContentType.objects.get_for_model(Message).pk, message.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "Secret plan", status_code=404)
        response = self.client.post(url, {"imagename": self._png("a.png", "red")})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Image.objects.exists())

    def test_deleted_article_is_staff_only(self):
        self.article.deleted = True
        self.article.save()
        url = self._url(self.article_ct.pk, self.article.pk)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.user.is_staff = True
        self.user.save()
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_upload_redirects_to_local_next(self):
        response = self._upload("pic.png")
        self.assertRedirects(
            response, "/wiki/edit/SomeArticle/", fetch_redirect_response=False
        )
        image = Image.objects.get(name="pic.png")
        self.assertEqual(image.content_object, self.article)

    def test_upload_does_not_redirect_offsite(self):
        edit_url = reverse("wiki_edit", kwargs={"title": "SomeArticle"})
        for i, next in enumerate(("//evil.example/", "https://evil.example/")):
            response = self._upload(f"pic{i}.png", next=next)
            self.assertRedirects(response, edit_url, fetch_redirect_response=False)

    def test_upload_does_not_overwrite_existing_file(self):
        self._upload("Main_Pic.png", "red")
        self._upload("Main Pic.png", "blue")
        first = Image.objects.get(name="Main_Pic.png")
        second = Image.objects.get(name="Main Pic.png")
        self.assertNotEqual(first.image.name, second.image.name)
        with PIL.Image.open(first.image.path) as img:
            self.assertEqual(img.getpixel((0, 0)), (255, 0, 0))
        with PIL.Image.open(second.image.path) as img:
            self.assertEqual(img.getpixel((0, 0)), (0, 0, 255))


# kann das weg??
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
    # kann das weg??
    # k = TestWlMarkdown_WikiWordsInLink_ExceptCorrectResult()
    # unittest.TextTestRunner().run(k)
