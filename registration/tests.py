from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from io import StringIO

import os
import sys

from participant.models import Troop
from registration.management.commands import create_users


class ImportUsersTestCase(TestCase):
    def tearDown(self):
        try:
            os.remove('test.csv')
        except OSError:
            pass

    def test_something(self):
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

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

        cmd = create_users.Command()
        cmd.import_lines(lines)

        self.assertEqual(
            3, get_user_model().objects.count(), 'not the right quantity of users was created'
        )

        self.assertEqual(
            2, Troop.objects.count(), 'not the right quantity of troops was created'
        )

    def test_successful_import(self):
        csv = 'troop_number;troop_name;firstname;lastname;email\n' \
              '130000;Diözesanverband München-Freising;Peter;Pan;peter.pan@dpsg1300.de\n' \
              '131700;Bezirk Ebersberg;Tom;Sawyer;tom.sawyer@pfadfinder-ebersberg.de\n' \
              '131700;Bezirk Ebersberg;Huckleberry;Finn;huckleberry.finn@pfadfinder-ebersberg.de\n'

        with open('test.csv', 'w') as test_csv:
            test_csv.write(csv)

        out = StringIO()

        call_command('create_users', 'test.csv', stdout=out)

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

    def test_missing_column_firstname(self):
        csv = 'troop_number;troop_name;lastname;email\n' \
              '130000;Diözesanverband München-Freising;Pan;peter.pan@dpsg1300.de\n' \
              '131700;Bezirk Ebersberg;Sawyer;tom.sawyer@pfadfinder-ebersberg.de\n' \
              '131700;Bezirk Ebersberg;Finn;huckleberry.finn@pfadfinder-ebersberg.de\n'

        with open('test.csv', 'w') as test_csv:
            test_csv.write(csv)

        out = StringIO()

        with self.assertRaises(CommandError):
            call_command('create_users', 'test.csv', stdout=out)

        self.assertEqual(0, get_user_model().objects.count(), 'users were created')
        self.assertEqual(0, Troop.objects.count(), 'troops were created')

    def test_missing_field_email(self):
        csv = 'troop_number;troop_name;firstname;lastname;email\n' \
              '130000;Diözesanverband München-Freising;Peter;Pan;peter.pan@dpsg1300.de\n' \
              '131700;Bezirk Ebersberg;Tom;Sawyer;tom.sawyer@pfadfinder-ebersberg.de\n' \
              '131700;Bezirk Ebersberg;Huckleberry;Finn\n'

        with open('test.csv', 'w') as test_csv:
            test_csv.write(csv)

        out = StringIO()
        err = StringIO()

        call_command('create_users', 'test.csv', stdout=out, stderr=err)

        self.assertEqual(2, get_user_model().objects.count(), 'users were created')
        self.assertEqual(2, Troop.objects.count(), 'troops were created')

    def test_duplicate_user_email(self):
        csv = 'troop_number;troop_name;firstname;lastname;email\n' \
              '130000;Diözesanverband München-Freising;Peter;Pan;peter.pan@dpsg1300.de\n' \
              '131700;Bezirk Ebersberg;Tom;Sawyer;peter.pan@dpsg1300.de\n' \
              '131700;Bezirk Ebersberg;Huckleberry;Finn;huckleberry.finn@pfadfinder-ebersberg.de\n'

        with open('test.csv', 'w') as test_csv:
            test_csv.write(csv)

        out = StringIO()
        err = StringIO()

        call_command('create_users', 'test.csv', stdout=out, stderr=err)

        self.assertEqual(2, get_user_model().objects.count(), 'users were created')
        self.assertEqual(2, Troop.objects.count(), 'troops were created')

    def test_double_create_users(self):
        csv = 'troop_number;troop_name;firstname;lastname;email\n' \
              '130000;Diözesanverband München-Freising;Peter;Pan;peter.pan@dpsg1300.de\n' \
              '131700;Bezirk Ebersberg;Tom;Sawyer;tom.sawyer@pfadfinder-ebersberg.de\n' \
              '131700;Bezirk Ebersberg;Huckleberry;Finn;huckleberry.finn@pfadfinder-ebersberg.de\n'

        with open('test.csv', 'w') as test_csv:
            test_csv.write(csv)

        out = StringIO()

        call_command('create_users', 'test.csv', stdout=out)
        call_command('create_users', 'test.csv', stdout=out)

        self.assertEqual(
            3, get_user_model().objects.count(), 'not the right quantity of users was created'
        )

        self.assertEqual(
            2, Troop.objects.count(), 'not the right quantity of troops was created'
        )
