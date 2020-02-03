from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from participant.models import Troop

import csv
import os


class Command(BaseCommand):
    help = 'Imports a set of users from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        try:
            with open(options['filename'], newline='') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                columns = self._extract_columns(next(csv_reader))

                lines = []

                for i, row in enumerate(csv_reader):
                    try:
                        line = {
                            'troop_number': row[columns['troop_number']],
                            'troop_name': row[columns['troop_name']],
                            'email': row[columns['email']],
                            'firstname': row[columns['firstname']],
                            'lastname': row[columns['lastname']],
                            'line_number': i+2,
                        }

                        lines.append(line)

                    except Exception as e:
                        self.stderr.write('Line {}: {}'.format(i+2, e.__cause__))

                self.import_lines(lines)

        except FileNotFoundError:
            raise CommandError('File {} not found'.format(os.path.abspath(options['filename'])))

    def import_lines(self, lines):
        created_users, created_troops = 0, 0

        for line in lines:
            try:
                troop, created = Troop.objects.get_or_create(
                    number=line['troop_number'],
                    name=line['troop_name'],
                )

                if created:
                    created_troops += 1

                user, created = get_user_model().objects.get_or_create(
                    email=line['email'],
                    first_name=line['firstname'],
                    last_name=line['lastname'],
                )

                if created:
                    created_users += 1

            except Exception as e:
                self.stderr.write('Line {}: {}'.format(line['line_number'], e.__cause__))

        self.stdout.write(f'Imported {created_troops} new troops and {created_users} new users')


    def _extract_columns(self, row) -> dict:
        required = ['email', 'firstname', 'lastname', 'troop_number', 'troop_name']
        missing = [name for name in required if name not in row]

        if missing:
            msg = 'Found the following columns in the csv: {}\n' \
                  'Required columns missing: {}'.format(', '.join(row), ', '.join(missing))
            raise CommandError(msg)

        return {name: i for i, name in enumerate(row)}