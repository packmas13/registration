# Setup

1. Make sure you Python 3.7+ installed
2. `git clone https://github.com/packmas13/registration.git`
3. `cd registration`
4. `python3 -m venv venv`
5. `source venv/bin/activate`
6. `pip3 install -r requirements.txt`
7. `python3 manage.py migrate`
8. `python3 manage.py compilemessages`

To create a backend user run `python3 manage.py createsuperuser`.

Finally, start the Django server with `python3 manage.py runserver` and head to [http://localhost:8000/](http://localhost:8000/).

# Hints

After changing models run `python3 manage.py makemigrations`.

After changing translations run `django-admin makemessages` in the corresponding submodule.
