manage=pipenv run python manage.py

dev: db.sqlite3 ## Run the local dev server under http://localhost:8000/
	$(manage) runserver

install: ## Install or update the python dependencies
	pipenv install

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
	pipenv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude migrations,__pycache__
	pipenv run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude migrations,__pycache__

MESSAGESDIRS = participant payment # Space separated modules with a translation

messages: $(MESSAGESDIRS) ## Update the translation files

$(MESSAGESDIRS):
	cd $@ && pipenv run django-admin makemessages

.DEFAULT_GOAL := help
.PHONY: help $(MESSAGESDIRS)

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

