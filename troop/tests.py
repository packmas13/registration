from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages

from nami import Nami, MemberNotFound
from nami.mock import Session as NamiMock

from .views import NamiSearchView


class IndexTest(TestCase):
    fixtures = ["troop_130000.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(email="user@test")
        self.client.force_login(self.user)

    def test_must_be_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("troop:index", kwargs={"troop_number": 404}))
        self.assertEqual(response.status_code, 302)

    def test_not_found(self):
        response = self.client.get(reverse("troop:index", kwargs={"troop_number": 404}))
        self.assertEqual(response.status_code, 403)

    def test_not_allowed(self):
        response = self.client.get(
            reverse("troop:index", kwargs={"troop_number": 130100})
        )
        self.assertEqual(response.status_code, 403)

    def test_found(self):
        response = self.client.get(
            reverse("troop:index", kwargs={"troop_number": 130000})
        )
        self.assertEqual(response.status_code, 200)


class CreateParticipantTest(TestCase):
    fixtures = ["troop_130000.json"]

    valid_data = {
        "troop": "1",  # id of the troop
        "first_name": "Trick",
        "last_name": "Duck",
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
            reverse("troop:participant.create", kwargs={"troop_number": 130000})
        )
        self.assertEqual(response.status_code, 200)

    def test_post_empty_form(self):
        response = self.client.post(
            reverse("troop:participant.create", kwargs={"troop_number": 130000})
        )
        self.assertEqual(response.status_code, 422)

    def test_post_form(self):
        response = self.client.post(
            reverse("troop:participant.create", kwargs={"troop_number": 130000}),
            self.valid_data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("troop:participant.index", kwargs={"troop_number": 130000}),
        )

    def test_post_form_addanother(self):
        data = self.valid_data.copy()
        data["_addanother"] = "1"
        response = self.client.post(
            reverse("troop:participant.create", kwargs={"troop_number": 130000}), data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("troop:participant.nami-search", kwargs={"troop_number": 130000}),
        )

    def test_get_form_prefilled(self):
        response = self.client.get(
            reverse("troop:participant.create", kwargs={"troop_number": 130000}),
            data={"first_name": "Trick"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Trick"')


class NamiSearchTest(TestCase):
    fixtures = ["troop_130000.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(email="user@test")
        self.client.force_login(self.user)
        self.original_nami_method = NamiSearchView.nami
        self.nami_mock = Nami({}, session_cls=NamiMock)
        self.mocked_nami_method = lambda s: self.nami_mock

    def tearDown(self):
        NamiSearchView.nami = self.original_nami_method

    def test_get_form(self):
        response = self.client.get(
            reverse("troop:participant.nami-search", kwargs={"troop_number": 130000})
        )
        self.assertEqual(response.status_code, 200)

    def test_post_empty_form(self):
        response = self.client.post(
            reverse("troop:participant.nami-search", kwargs={"troop_number": 130000})
        )
        self.assertEqual(response.status_code, 422)

    def test_post_form(self):
        self.nami_mock.session.response = [
            {
                "entries_nachname": "Duck",
                "entries_vorname": "Trick",
                "entries_mitgliedsNummer": 12345,
            }
        ]
        NamiSearchView.nami = self.mocked_nami_method

        response = self.client.post(
            reverse("troop:participant.nami-search", kwargs={"troop_number": 130000}),
            {"nami": "12345"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("troop:participant.create", kwargs={"troop_number": 130000})
            + "?last_name=Duck&first_name=Trick&nami=12345",
        )
        m = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(1, len(m))
        self.assertEqual(messages.SUCCESS, m[0].level)

    def test_post_form_empty_nami_settings(self):
        response = self.client.post(
            reverse("troop:participant.nami-search", kwargs={"troop_number": 130000}),
            {"nami": "12345"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("troop:participant.create", kwargs={"troop_number": 130000})
            + "?nami=12345",
        )
        m = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(1, len(m))
        self.assertEqual(messages.WARNING, m[0].level)

    def test_post_not_found(self):
        self.nami_mock.session.exception = MemberNotFound
        NamiSearchView.nami = self.mocked_nami_method

        response = self.client.post(
            reverse("troop:participant.nami-search", kwargs={"troop_number": 130000}),
            {"nami": "12345"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("troop:participant.create", kwargs={"troop_number": 130000})
            + "?nami=12345",
        )
        m = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(1, len(m))
        self.assertEqual(messages.INFO, m[0].level)

    def test_post_form_already_in_db(self):
        response = self.client.post(
            reverse("troop:participant.nami-search", kwargs={"troop_number": 130000}),
            {"nami": "130001"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("troop:participant.edit", kwargs={"troop_number": 130000, "pk": 1}),
        )
        m = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(1, len(m))
        self.assertEqual(messages.INFO, m[0].level)

    def test_post_form_already_in_db_wrong_troop(self):
        response = self.client.post(
            reverse("troop:participant.nami-search", kwargs={"troop_number": 130000}),
            {"nami": "130002"},
        )
        self.assertEqual(response.status_code, 409)
        m = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(1, len(m))
        self.assertEqual(messages.ERROR, m[0].level)


class IndexParticipantTest(TestCase):
    fixtures = ["troop_130000.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(email="user@test")
        self.client.force_login(self.user)

    def test_found(self):
        response = self.client.get(
            reverse("troop:participant.index", kwargs={"troop_number": 130000})
        )
        self.assertEqual(response.status_code, 200)

    def test_contains_creations(self):
        response = self.client.get(
            reverse("troop:participant.index", kwargs={"troop_number": 130000})
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Trick")

        self.client.post(
            reverse("troop:participant.create", kwargs={"troop_number": 130000}),
            CreateParticipantTest.valid_data,
        )

        response = self.client.get(
            reverse("troop:participant.index", kwargs={"troop_number": 130000})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trick")


class ParticipantExportTest(TestCase):
    fixtures = ["troop_130000.json"]

    def setUp(self):
        self.user = get_user_model().objects.get(email="user@test")
        self.client.force_login(self.user)

    def test_export(self):
        response = self.client.get(
            reverse("troop:participant.export", kwargs={"troop_number": 130000})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "text/csv")
        self.assertEqual(
            response["content-disposition"],
            'attachment; filename="packmas13_130000.csv"',
        )
        self.assertContains(response, "Vor")
        self.assertContains(response, "Nach")
        self.assertContains(response, "no section")
        self.assertContains(response, "2020-02-20")
