from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from mainpage.views import get_chieftains


class LocaleViewTest(TestCase):
    def test_anonymous_users_do_not_see_server_details(self):
        response = self.client.get("/locale/")

        self.assertEqual(response.status_code, 302)
        self.assertNotContains(response, "Server time", status_code=302)

    def test_staff_sees_server_details(self):
        self.client.force_login(User.objects.create_user("staff", is_staff=True))

        self.assertContains(self.client.get("/locale/"), "Server time")


class ChieftainsTest(TestCase):
    @override_settings(WIDELANDS_SVN_DIR="/nonexistent/", INQUIRY_CHIEFTAINS=["Chief"])
    def test_fallback_list_does_not_grow(self):
        get_chieftains()
        chieftains = get_chieftains()

        self.assertEqual(chieftains[0], "Chief")
        self.assertEqual(len(chieftains), 3)
