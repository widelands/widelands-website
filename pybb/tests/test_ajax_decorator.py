import json

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


class TestAjaxDecoratorErrorHandling(TestCase):
    """The @ajax decorator must not leak tracebacks to the client."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.client.login(username="testuser", password="pass")

    def _post_preview(self, **kwargs):
        return self.client.post(
            reverse("pybb_post_ajax_preview"),
            # An invalid markup value will not trigger an exception by itself,
            # but missing 'content' with a valid markup also won't.  We need
            # to provoke an actual exception inside the view.  Passing a
            # markup value that passes the allowlist check but causes an error
            # later is hard, so instead we test indirectly: post valid data
            # and verify the error-path contract via a dedicated unit test of
            # the decorator below.
            **kwargs,
        )

    def test_error_response_hides_traceback_in_production(self):
        """When DEBUG=False, error responses must not contain traceback details."""
        from pybb.util import ajax

        @ajax
        def exploding_view(request):
            raise ValueError("secret internal details")

        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.post("/fake/")

        with override_settings(DEBUG=False):
            response = exploding_view(request)

        body = json.loads(response.content)
        self.assertIn("error", body)
        self.assertNotIn("secret internal details", body["error"])
        self.assertNotIn("Traceback", body["error"])

    def test_error_response_includes_traceback_in_debug(self):
        """When DEBUG=True, the traceback should be available for developers."""
        from pybb.util import ajax

        @ajax
        def exploding_view(request):
            raise ValueError("secret internal details")

        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.post("/fake/")

        with override_settings(DEBUG=True):
            response = exploding_view(request)

        body = json.loads(response.content)
        self.assertIn("error", body)
        self.assertIn("secret internal details", body["error"])
