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

After changing models run `make migrations` to update the migrations files.

After changing translations run `make messages` in the corresponding submodule.

To add a dependency, run `pipenv install [dependency]` (add the `--dev` flag for dev-only dependencies).
