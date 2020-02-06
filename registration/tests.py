from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from io import StringIO

from participant.models import Troop
from registration.management.commands import create_users


class ImportUsersTestCase(TestCase):
    def test_csv_import(self):
        call_command('create_users', 'registration/test.csv', stdout=StringIO())

        self.assertEqual(
            3, get_user_model().objects.count(), 'not the right quantity of users was created'
        )

        self.assertEqual(
            2, Troop.objects.count(), 'not the right quantity of troops was created'
        )

        troop = Troop.objects.get(number=131700)
        self.assertEqual('Bezirk Ebersberg', troop.name)

        troop = Troop.objects.get(name='Diözesanverband München-Freising')
        self.assertEqual(130000, troop.number)

        user = get_user_model().objects.get(email='peter.pan@dpsg1300.de')
        self.assertEqual('Peter', user.first_name)
        self.assertEqual('Pan', user.last_name)
        self.assertEqual(1, user.troops.count())

    def test_missing_column_firstname(self):
        lines = [
            {
                'troop_number': 130000,
                'troop_name': 'Diözesanverband München-Freising',
                'lastname': 'Pan',
                'email': 'peter.pan@dpsg1300.de',
                'line_number': 1,
            },
            {
                'troop_number': 131700,
                'troop_name': 'Bezirk Ebersberg',
                'lastname': 'Sawyer',
                'email': 'tom.sawyer@pfadfinder-ebersberg.de',
                'line_number': 2,
            },
            {
                'troop_number': 131700,
                'troop_name': 'Bezirk Ebersberg',
                'lastname': 'Finn',
                'email': 'huckleberry.finn@pfadfinder-ebersberg.de',
                'line_number': 3,
            },
        ]

        cmd = create_users.Command(stdout=StringIO(), stderr=StringIO())
        cmd.import_lines(lines)

        self.assertEqual(0, get_user_model().objects.count(), 'users were created')
        self.assertEqual(2, Troop.objects.count(), 'troops were created')

    def test_missing_field_email(self):
        lines = [
            {
                'troop_number': 130000,
                'troop_name': 'Diözesanverband München-Freising',
                'firstname': 'Peter',
                'lastname': 'Pan',
                'email': 'peter.pan@dpsg1300.de',
                'line_number': 1,
            },
            {
                'troop_number': 131700,
                'troop_name': 'Bezirk Ebersberg',
                'firstname': 'Tom',
                'lastname': 'Sawyer',
                'email': 'tom.sawyer@pfadfinder-ebersberg.de',
                'line_number': 2,
            },
            {
                'troop_number': 131700,
                'troop_name': 'Bezirk Ebersberg',
                'firstname': 'Huckleberry',
                'lastname': 'Finn',
                'line_number': 3,
            },
        ]

        cmd = create_users.Command(stdout=StringIO(), stderr=StringIO())
        cmd.import_lines(lines)

        self.assertEqual(
            2, get_user_model().objects.count(), 'not the right quantity of users was created'
        )

        self.assertEqual(
            2, Troop.objects.count(), 'not the right quantity of troops was created'
        )

    def test_duplicate_user_email(self):
        lines = [
            {
                'troop_number': 130000,
                'troop_name': 'Diözesanverband München-Freising',
                'firstname': 'Peter',
                'lastname': 'Pan',
                'email': 'peter.pan@dpsg1300.de',
                'line_number': 1,
            },
            {
                'troop_number': 131700,
                'troop_name': 'Bezirk Ebersberg',
                'firstname': 'Tom',
                'lastname': 'Sawyer',
                'email': 'peter.pan@dpsg1300.de',
                'line_number': 2,
            },
            {
                'troop_number': 131700,
                'troop_name': 'Bezirk Ebersberg',
                'firstname': 'Huckleberry',
                'lastname': 'Finn',
                'email': 'huckleberry.finn@pfadfinder-ebersberg.de',
                'line_number': 3,
            },
        ]

        cmd = create_users.Command(stdout=StringIO(), stderr=StringIO())
        cmd.import_lines(lines)

        self.assertEqual(
            2, get_user_model().objects.count(), 'not the right quantity of users was created'
        )

        self.assertEqual(
            2, Troop.objects.count(), 'not the right quantity of troops was created'
        )

    def test_importing_twice(self):
        lines = [
            {
                'troop_number': 130000,
                'troop_name': 'Diözesanverband München-Freising',
                'firstname': 'Peter',
                'lastname': 'Pan',
                'email': 'peter.pan@dpsg1300.de',
                'line_number': 1,
            },
            {
                'troop_number': 131700,
                'troop_name': 'Bezirk Ebersberg',
                'firstname': 'Tom',
                'lastname': 'Sawyer',
                'email': 'tom.sawyer@pfadfinder-ebersberg.de',
                'line_number': 2,
            },
            {
                'troop_number': 131700,
                'troop_name': 'Bezirk Ebersberg',
                'firstname': 'Huckleberry',
                'lastname': 'Finn',
                'email': 'huckleberry.finn@pfadfinder-ebersberg.de',
                'line_number': 3,
            },
        ]

        cmd = create_users.Command(stdout=StringIO(), stderr=StringIO())
        cmd.import_lines(lines)
        cmd.import_lines(lines)

        self.assertEqual(
            3, get_user_model().objects.count(), 'not the right quantity of users was created'
        )

        self.assertEqual(
            2, Troop.objects.count(), 'not the right quantity of troops was created'
        )
