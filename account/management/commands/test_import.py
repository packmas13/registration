from io import StringIO
from django.core.management import call_command
from django.test import TestCase

from ...models import User

from participant.models.troop import Troop


class ImportUsersTest(TestCase):
    def test_fake_import(self):
        # Ensure the DB is empty
        self.assertEqual(0, User.objects.count())

        out = StringIO()
        call_command(
            "importusers", "account/management/commands/users_example.csv", stdout=out
        )

        self.assertEqual(
            3, User.objects.count(), "not the right quantity of users were created"
        )
        self.assertEqual(
            2, Troop.objects.count(), "not the right quantity of troops were created"
        )

        first_troop = Troop.objects.get(number=1300)
        self.assertEqual("Scout of the world", first_troop.name)
        self.assertEqual(2, first_troop.users.count())

        jane = User.objects.get(email="jane@example.com")
        self.assertEqual(2, jane.troops.count())
