from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class IndexTest(TestCase):
    fixtures = ["troop_130000.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(email="user@test")
        self.client.force_login(self.user)

    def test_must_be_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("troop:index", kwargs={"troop": 404}))
        self.assertEqual(response.status_code, 302)

    def test_not_found(self):
        response = self.client.get(reverse("troop:index", kwargs={"troop": 404}))
        self.assertEqual(response.status_code, 403)

    def test_not_allowed(self):
        response = self.client.get(reverse("troop:index", kwargs={"troop": 130100}))
        self.assertEqual(response.status_code, 403)

    def test_found(self):
        response = self.client.get(reverse("troop:index", kwargs={"troop": 130000}))
        self.assertEqual(response.status_code, 200)


class CreateParticipantTest(TestCase):
    fixtures = ["troop_130000.json"]

    valid_data = {
        "troop": "1",  # id of the troop
        "firstname": "Trick",
        "lastname": "Duck",
        "gender": "male",
        "birthday": "1.1.1900",
        # "email": "", not required
        "nami": "12",
        "age_section": "cub",
        # "is_leader": "", not required
        "attendance": [1],  # id of the day
        # "diet": "", not required
        # "medication": "", not required
        # "comment": "", not required
    }

    def setUp(self):
        self.user = get_user_model().objects.get(email="user@test")
        self.client.force_login(self.user)

    def test_get_form(self):
        response = self.client.get(
            reverse("troop:participant.create", kwargs={"troop": 130000})
        )
        self.assertEqual(response.status_code, 200)

    def test_post_empty_form(self):
        response = self.client.post(
            reverse("troop:participant.create", kwargs={"troop": 130000})
        )
        self.assertEqual(response.status_code, 422)

    def test_post_form(self):
        response = self.client.post(
            reverse("troop:participant.create", kwargs={"troop": 130000}), self.valid_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("troop:participant.index", kwargs={"troop": 130000})
        )

    def test_post_form_addanother(self):
        data = self.valid_data.copy()
        data["_addanother"] = "1"
        response = self.client.post(
            reverse("troop:participant.create", kwargs={"troop": 130000}), data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("troop:participant.create", kwargs={"troop": 130000})
        )


class IndexParticipantTest(TestCase):
    fixtures = ["troop_130000.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(email="user@test")
        self.client.force_login(self.user)

    def test_found(self):
        response = self.client.get(
            reverse("troop:participant.index", kwargs={"troop": 130000})
        )
        self.assertEqual(response.status_code, 200)

    def test_contains_creations(self):
        response = self.client.get(
            reverse("troop:participant.index", kwargs={"troop": 130000})
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Trick")

        self.client.post(
            reverse("troop:participant.create", kwargs={"troop": 130000}),
            CreateParticipantTest.valid_data,
        )

        response = self.client.get(
            reverse("troop:participant.index", kwargs={"troop": 130000})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trick")
