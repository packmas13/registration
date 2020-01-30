import csv
from django.core.management.base import BaseCommand, CommandError


from ...models import User
from participant.models.troop import Troop


class Command(BaseCommand):
    help = "Import a csv file of users in the database"

    def add_arguments(self, parser):
        parser.add_argument("filepath", type=str)

    def handle(self, *args, **options):
        # import os
        with open(options["filepath"]) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")

            columns = self._extract_columns(next(csv_reader))
            created_users = 0
            created_troops = 0
            for row in csv_reader:
                user, created = User.objects.get_or_create(email=row[columns["email"]])
                if created:
                    created_users += 1
                    pass
                    # TODO: trigger an event to send an email

                troop, created = Troop.objects.get_or_create(
                    number=row[columns["troop_number"]],
                    defaults={"name": row[columns["troop_name"]]},
                )
                if created:
                    created_troops += 1
                troop.users.add(user)

        self.stdout.write(
            f"{created_troops} new Troops\n{created_users} new Users"
        )

    def _extract_columns(self, row) -> dict:
        required = ["email", "troop_number", "troop_name"]
        missing = [name for name in required if name not in row]
        if missing:
            msg = "Found the following columns in the csv: "
            msg += ", ".join(row)
            msg += "\nRequired columns missing: "
            msg += ", ".join(missing)
            raise CommandError(msg)
        return {name: i for i, name in enumerate(row)}
