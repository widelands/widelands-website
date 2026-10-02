import io
import os
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image

from pybb import settings as pybb_settings
from pybb.models import Attachment, Post
from pybb.tests.test_views import _ForumTestBase


def _png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (2, 2)).save(buf, format="PNG")
    return buf.getvalue()


class _AttachmentTestBase(_ForumTestBase):
    def setUp(self):
        super().setUp()
        media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media_root)
        media_override = override_settings(MEDIA_ROOT=media_root)
        media_override.enable()
        self.addCleanup(media_override.disable)
        os.makedirs(os.path.join(media_root, pybb_settings.ATTACHMENT_UPLOAD_TO))

        self.post = self.topic.posts.first()

    def _attach(self, name, content_type, data, post=None):
        attachment = Attachment(
            post=post or self.post,
            size=len(data),
            content_type=content_type,
            name=name,
            path=name,
        )
        with open(attachment.get_absolute_path(), "wb") as f:
            f.write(data)
        attachment.save()
        return attachment

    def _get(self, attachment):
        return self.client.get(attachment.get_absolute_url())


class TestAttachmentContentType(_AttachmentTestBase):
    def test_html_is_downloaded_not_rendered(self):
        attachment = self._attach(
            "evil.txt", "text/html", b"<script>alert(document.cookie)</script>"
        )
        response = self._get(attachment)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/octet-stream")
        self.assertEqual(
            response["Content-Disposition"], 'attachment; filename="evil.txt"'
        )
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

    def test_image_is_shown_inline(self):
        data = _png_bytes()
        attachment = self._attach("pic.png", "image/png", data)
        response = self._get(attachment)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertEqual(response["Content-Disposition"], 'inline; filename="pic.png"')
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(b"".join(response.streaming_content), data)


class TestAttachmentAccess(_AttachmentTestBase):
    def test_internal_forum_attachment_hidden_from_regular_user(self):
        self.category.internal = True
        self.category.save()
        attachment = self._attach("notes.txt", "text/plain", b"internal")

        self.assertEqual(self._get(attachment).status_code, 404)
        self.client.login(username="regular", password="pass")
        self.assertEqual(self._get(attachment).status_code, 404)

        self.regular_user.user_permissions.add(
            Permission.objects.get(codename="can_access_internal")
        )
        self.assertEqual(self._get(attachment).status_code, 200)

    def test_hidden_post_attachment_only_for_moderators(self):
        self.post.hidden = True
        self.post.save()
        attachment = self._attach("spam.txt", "text/plain", b"spam")

        self.client.login(username="regular", password="pass")
        self.assertEqual(self._get(attachment).status_code, 404)
        self.client.login(username="moderator", password="pass")
        self.assertEqual(self._get(attachment).status_code, 200)


class TestAttachmentUpload(_AttachmentTestBase):
    def test_stored_type_is_detected_not_taken_from_browser(self):
        for i in range(settings.ALLOW_ATTACHMENTS_AFTER):
            Post.objects.create(
                topic=self.topic, user=self.regular_user, body=f"post {i}"
            )
        self.client.login(username="regular", password="pass")
        # .wai files skip the MIME comparison in validate_file, so the browser
        # supplied type is not checked at all.
        wai = "".join(f"[{s}]\n" for s in settings.ALLOWED_WAI_SECTIONS).encode()
        upload = SimpleUploadedFile("ai.wai", wai, content_type="text/html")

        self.client.post(
            reverse("pybb_add_post", args=[self.topic.id]),
            {"body": "see attachment", "markup": "markdown", "attachment": upload},
        )

        attachment = Attachment.objects.get(name="ai.wai")
        self.assertEqual(attachment.content_type, "text/plain")
