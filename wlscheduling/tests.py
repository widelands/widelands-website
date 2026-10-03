from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from wlscheduling.models import Availabilities
from wlscheduling.views import TIME_FORMAT


def _hour(days_ahead, hour=12):
    t = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    return t.replace(hour=hour) + timedelta(days=days_ahead)


class SchedulingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("player")
        self.client.force_login(self.user)
        self.url = reverse("scheduling_scheduling")

    def _post(self, times):
        return self.client.post(
            self.url, {str(i): t.strftime(TIME_FORMAT) for i, t in enumerate(times)}
        )

    def _stored(self):
        return set(
            Availabilities.objects.filter(user=self.user).values_list(
                "avail_time", flat=True
            )
        )

    def test_post_replaces_availabilities(self):
        Availabilities.objects.create(user=self.user, avail_time=_hour(1))
        Availabilities.objects.create(user=self.user, avail_time=_hour(2))

        self._post([_hour(2), _hour(3)])

        self.assertEqual(self._stored(), {_hour(2), _hour(3)})

    def test_past_and_far_future_times_are_not_stored(self):
        self._post([_hour(-1), _hour(3), _hour(400)])

        self.assertEqual(self._stored(), {_hour(3)})

    def test_malformed_time_is_rejected(self):
        response = self.client.post(self.url, {"0": "tomorrow"})

        self.assertEqual(response.status_code, 400)

    def _count_queries(self, request):
        with CaptureQueriesContext(connection) as queries:
            request()
        return len(queries)

    def test_queries_do_not_grow_with_number_of_entries(self):
        times = [_hour(day, hour) for day in range(1, 11) for hour in range(24)]
        other = User.objects.create_user("other")
        for t in times:
            Availabilities.objects.create(user=other, avail_time=t)
        self._post(times[:1])

        few = self._count_queries(lambda: self._post(times[:2]))
        many = self._count_queries(lambda: self._post(times))

        self.assertEqual(len(self._stored()), len(times))
        self.assertEqual(few, many)

    def test_find_queries_do_not_grow_with_number_of_users(self):
        url = reverse("scheduling_find")
        self.client.get(url)
        user = User.objects.create_user("other")
        Availabilities.objects.create(user=user, avail_time=_hour(1))
        one = self._count_queries(lambda: self.client.get(url))

        for i in range(10):
            user = User.objects.create_user(f"other{i}")
            Availabilities.objects.create(user=user, avail_time=_hour(1))
        many = self._count_queries(lambda: self.client.get(url))

        self.assertEqual(one, many)
