# Setup

1. Make sure you have Python 3.7+ and [pipenv](https://github.com/pypa/pipenv) installed
2. `git clone https://github.com/packmas13/registration.git`
3. `cd registration`

# Run local server

```
make dev
```

The first time, it will prompt you to create a backend user (you can create other users later with `make superuser`).

Finally, the Django server should be running and accessible under [http://localhost:8000/](http://localhost:8000/).

# Update local server

1. `git pull`
2. `make install` in case of new dependencies
3. `make migrate` in case of new migrations
4. `make compilemessages` in case of new translated messages
5. `make dev`

# Hints

Run `make lint` to format your files using [black](https://github.com/psf/black).

After changing models run `make migrations` to generate the migrations files and `make migrate`.

After changing translated text run `make messages` to update the localization files (`.po`), update the translations and run `make compilemessages`.

Emails are sent to stdout instead of a SMTP server when run in debug mode.

To add a dependency, run `pipenv install [dependency]` (add the `--dev` flag for dev-only dependencies).

# Import of users and scout troops

There is a custom management command to import a batch of users and scout troops and associate users with their respective troops:

```
python3 manage.py create_users <file.csv> [--send-emails]
```

Have a look at `registration/test.csv` for the structure of the file.

# Styling

[Tailwindcss](https://tailwindcss.com/) "utility-framework" is used for the styling.