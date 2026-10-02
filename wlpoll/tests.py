from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from wlpoll.models import Choice, Poll, Vote


class PollTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.poll = Poll.objects.create(name="Best tribe?")
        cls.choice = Choice.objects.create(poll=cls.poll, choice="Barbarians")
        cls.other_choice = Choice.objects.create(poll=cls.poll, choice="Empire")
        cls.user = User.objects.create_user("voter")

    def _vote(self, choice_id):
        return self.client.post(
            reverse("wlpoll_vote", args=(self.poll.id,)), {"choice_id": choice_id}
        )


class VoteTest(PollTestCase):
    def setUp(self):
        self.client.force_login(self.user)

    def test_vote_is_counted_once(self):
        self._vote(self.choice.id)
        response = self._vote(self.other_choice.id)

        self.assertEqual(response.status_code, 403)
        self.choice.refresh_from_db()
        self.other_choice.refresh_from_db()
        self.assertEqual((self.choice.votes, self.other_choice.votes), (1, 0))

    def test_database_rejects_second_vote_of_a_user(self):
        # Parallel requests both pass the "already voted" check in the view
        Vote.objects.create(user=self.user, poll=self.poll, choice=self.choice)
        with self.assertRaises(IntegrityError):
            Vote.objects.create(
                user=self.user, poll=self.poll, choice=self.other_choice
            )

    def test_invalid_choice_id_is_ignored(self):
        response = self._vote("abc")

        self.assertRedirects(response, self.poll.get_absolute_url())
        self.assertFalse(Vote.objects.exists())


class DisplayPollTest(PollTestCase):
    def test_poll_texts_cannot_break_out_of_the_script(self):
        Poll.objects.filter(pk=self.poll.pk).update(
            name="</script><script>alert(1)</script>"
        )
        Choice.objects.filter(pk=self.choice.pk).update(choice="\\'];alert(2);//")

        response = self.client.get(self.poll.get_absolute_url())

        self.assertNotContains(response, "<script>alert(1)")
        self.assertNotContains(response, "alert(2);//'")
        self.assertContains(response, "\\u003C/script\\u003E\\u003Cscript\\u003E")
