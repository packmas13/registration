manage=pipenv run python manage.py

dev: db.sqlite3 ## Run the local dev server under http://localhost:8000/
	$(manage) runserver

install: ## Install or update the python dependencies
	pipenv install

install-dev: ## Install or update the python dependencies for development
	pipenv install --dev

db.sqlite3: # if this file is not present, install everything
	@$(MAKE) install migrate compilemessages superuser

superuser: ## Create a backend user
	$(manage) createsuperuser

migrate: ## Run the database migrations
	$(manage) migrate

migrations: ## Create migrations after a model has been changed
	$(manage) makemigrations

compilemessages: ## Compile the translated messages
	$(manage) compilemessages

test: ## Run the tests
	$(manage) test

lint:
	pipenv run black --target-version=py37 --exclude migrations/ .

lintcheck:
	# Fail if the code should be linted (fix it with "make lint")
	pipenv run black --target-version=py37 --exclude migrations/ --check .
	# Fail if there are Python syntax errors or undefined names
	pipenv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude migrations,__pycache__
	# Print some warnings (without failing, thanks to exit-zero).
	# The GitHub editor is 127 chars wide.
	pipenv run flake8 . --count --exit-zero --ignore=E231,E203,W503 --per-file-ignores='__init__.py:F401' --max-complexity=10 --max-line-length=127 --statistics --exclude migrations,__pycache__

MESSAGESDIRS = participant payment # Space separated modules with a translation

messages: $(MESSAGESDIRS) ## Update the translation files

$(MESSAGESDIRS):
	cd $@ && pipenv run django-admin makemessages

.DEFAULT_GOAL := help
.PHONY: help $(MESSAGESDIRS)

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

