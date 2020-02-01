from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from participant.models import Troop

import csv


class Command(BaseCommand):
    help = 'Imports a set of users from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        created_users, created_troops = 0, 0

        try:
            with open(options['filename'], newline='') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                columns = self._extract_columns(next(csv_reader))

                with transaction.atomic():
                    for i, row in enumerate(csv_reader):
                        try:
                            if not Troop.objects.filter(number=row[columns['troop_number']]).exists():
                                t = Troop()

                                t.number = row[columns['troop_number']]
                                t.name = row[columns['troop_name']]

                                t.save()
                                created_troops += 1

                            user = get_user_model().objects.create_user(email=row[columns['email']])

                            user.is_active = False
                            user.first_name = row[columns['firstname']]
                            user.last_name = row[columns['lastname']]

                            user.save()
                            created_users += 1
                        except Exception as e:
                            raise CommandError('Line {}: {}'.format(i+2, e.__cause__))
        except FileNotFoundError:
            raise CommandError('File not found')

        self.stdout.write(f'Imported {created_troops} new troops and {created_users} new users successfully')

    def _extract_columns(self, row) -> dict:
        required = ['email', 'firstname', 'lastname', 'troop_number', 'troop_name']
        missing = [name for name in required if name not in row]

        if missing:
            msg = 'Found the following columns in the csv: {}\n' \
                  'Required columns missing: {}'.format(', '.join(row), ', '.join(missing))
            raise CommandError(msg)

        return {name: i for i, name in enumerate(row)}
