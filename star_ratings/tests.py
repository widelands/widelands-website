from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from star_ratings.models import Rating, UserRating
from wlmaps.models import Map


class RateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="rater", password="pw")
        self.map = Map.objects.create(
            name="Map",
            author="Author",
            w=64,
            h=64,
            nr_players=2,
            descr="description",
            minimap="/wlmaps/minimaps/Map.png",
            uploader=self.user,
        )
        self.url = reverse(
            "ratings:rate",
            args=(ContentType.objects.get_for_model(Map).pk, self.map.pk),
        )

    def rating(self):
        return Rating.objects.for_instance(self.map)

    def test_anonymous_user_is_sent_to_login(self):
        response = self.client.post(self.url, {"score": 5, "next": "/maps/"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])
        self.assertFalse(UserRating.objects.exists())

    def test_rating_redirects_to_local_next(self):
        self.client.login(username="rater", password="pw")
        response = self.client.post(self.url, {"score": 5, "next": "/maps/map/"})
        self.assertRedirects(response, "/maps/map/", fetch_redirect_response=False)
        self.assertEqual(self.rating().average, 5)

    def test_foreign_next_is_not_followed(self):
        self.client.login(username="rater", password="pw")
        for next_url in ("https://evil.example/", "//evil.example/"):
            response = self.client.post(self.url, {"score": 5, "next": next_url})
            self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_rater_ip_is_not_recorded(self):
        self.client.login(username="rater", password="pw")
        self.client.post(self.url, {"score": 5}, HTTP_X_REAL_IP="203.0.113.7")
        self.assertIsNone(UserRating.objects.get().ip)

    def test_score_outside_range_is_rejected(self):
        self.client.login(username="rater", password="pw")
        for score in (0, 11, 32767):
            response = self.client.post(
                self.url,
                {"score": score},
                content_type="application/json",
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )
            self.assertEqual(response.status_code, 400)
        self.assertFalse(UserRating.objects.exists())

    def test_ajax_rerating_replaces_the_previous_score(self):
        other = User.objects.create_user(username="other", password="pw")
        Rating.objects.rate(self.map, 2, user=other)
        self.client.login(username="rater", password="pw")
        for score in (10, 6):
            response = self.client.post(
                self.url,
                {"score": score, "next": "/maps/map/"},
                content_type="application/json",
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "count": 2,
                "total": 8,
                "average": 4.0,
                "percentage": 40.0,
                "user_rating": 6,
            },
        )
        self.assertEqual(UserRating.objects.get(user=self.user).score, 6)
