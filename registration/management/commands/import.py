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
        try:
            with open(options['filename'], newline='') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=';')

                with transaction.atomic():
                    for i, row in enumerate(csvreader):
                        try:
                            t = Troop()

                            t.number = row[0]
                            t.name = row[1]

                            t.save()

                            user = get_user_model().objects.create_user(email=row[4])

                            user.is_active = False
                            user.first_name = row[2]
                            user.last_name = row[3]

                            user.save()
                        except Exception as e:
                            self.stderr.write(self.style.ERROR('Line {}: {}'.format(i+1, e.__cause__)))
                            return
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR('File not found'))
