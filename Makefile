CURRENT_DIRECTORY := $(shell pwd)

TESTSCOPE = apps
TESTFLAGS = --with-timer --timer-top-n 10 --keepdb

start:
	@docker-compose up --build --d

stop:
	@docker-compose stop

restart: stop start

recreate:
	@docker-compose up --build --d --force-recreate

clean: stop
	@docker-compose rm --force
	@find . -name \*.pyc -delete
	
logs:
	@docker-compose logs -f
	
migrations:
	@docker-compose run --rm ssh_controller python ./manage.py makemigrations app

migrate:
	@docker-compose run --rm ssh_controller python ./manage.py migrate

createsuperuser:
	@docker-compose run --rm ssh_controller python ./manage.py createsuperuser

.PHONY: start stop restart recreate clean logs migrations migrate createsuperuser
