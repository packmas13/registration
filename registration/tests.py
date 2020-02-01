from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from participant.models import Troop

import os
from io import StringIO


class ImportUsersTestCase(TestCase):
    def tearDown(self):
        try:
            os.remove('test.csv')
        except OSError:
            pass

    def test_successful_import(self):
        csv = 'troop_number;troop_name;firstname;lastname;email\n' \
              '130000;Diözesanverband München-Freising;Peter;Pan;peter.pan@dpsg1300.de\n' \
              '131700;Bezirk Ebersberg;Tom;Sawyer;tom.sawyer@pfadfinder-ebersberg.de\n' \
              '131700;Bezirk Ebersberg;Huckleberry;Finn;huckleberry.finn@pfadfinder-ebersberg.de\n'

        with open('test.csv', 'w') as test_csv:
            test_csv.write(csv)

        out = StringIO()

        call_command('import', 'test.csv', stdout=out)

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

    def test_missing_firstname_column(self):
        csv = 'troop_number;troop_name;lastname;email\n' \
              '130000;Diözesanverband München-Freising;Pan;peter.pan@dpsg1300.de\n' \
              '131700;Bezirk Ebersberg;Sawyer;tom.sawyer@pfadfinder-ebersberg.de\n' \
              '131700;Bezirk Ebersberg;Finn;huckleberry.finn@pfadfinder-ebersberg.de\n'

        with open('test.csv', 'w') as test_csv:
            test_csv.write(csv)

        out = StringIO()

        with self.assertRaises(CommandError):
            call_command('import', 'test.csv', stdout=out)

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

        with self.assertRaises(CommandError):
            call_command('import', 'test.csv', stdout=out)

        self.assertEqual(0, get_user_model().objects.count(), 'users were created')
        self.assertEqual(0, Troop.objects.count(), 'troops were created')

    def test_duplicate_user_email(self):
        csv = 'troop_number;troop_name;firstname;lastname;email\n' \
              '130000;Diözesanverband München-Freising;Peter;Pan;peter.pan@dpsg1300.de\n' \
              '131700;Bezirk Ebersberg;Tom;Sawyer;peter.pan@dpsg1300.de\n' \
              '131700;Bezirk Ebersberg;Huckleberry;Finn;huckleberry.finn@pfadfinder-ebersberg.de\n'

        with open('test.csv', 'w') as test_csv:
            test_csv.write(csv)

        out = StringIO()

        with self.assertRaises(CommandError):
            call_command('import', 'test.csv', stdout=out)

        self.assertEqual(0, get_user_model().objects.count(), 'users were created')
        self.assertEqual(0, Troop.objects.count(), 'troops were created')

    def test_double_import(self):
        csv = 'troop_number;troop_name;firstname;lastname;email\n' \
              '130000;Diözesanverband München-Freising;Peter;Pan;peter.pan@dpsg1300.de\n' \
              '131700;Bezirk Ebersberg;Tom;Sawyer;tom.sawyer@pfadfinder-ebersberg.de\n' \
              '131700;Bezirk Ebersberg;Huckleberry;Finn;huckleberry.finn@pfadfinder-ebersberg.de\n'

        with open('test.csv', 'w') as test_csv:
            test_csv.write(csv)

        out = StringIO()

        call_command('import', 'test.csv', stdout=out)

        with self.assertRaises(CommandError):
            call_command('import', 'test.csv', stdout=out)

        self.assertEqual(
            3, get_user_model().objects.count(), 'not the right quantity of users was created'
        )

        self.assertEqual(
            2, Troop.objects.count(), 'not the right quantity of troops was created'
        )
