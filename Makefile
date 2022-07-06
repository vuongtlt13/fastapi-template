migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

# usage: make migration-generate <filename>
migration-generate:
	alembic revision --autogenerate -m "$(word 1, $(filter-out $@,$(MAKECMDGOALS)))"

generate-secret:
	python ./app/scripts/generate_secret_key.py

db-seed:
	python ./app/scripts/initial_data.py

start-app:
	uvicorn main:app --reload

ifeq ($(WORKER),)
WORKER := 1
endif
ifeq ($(HOST),)
HOST := 127.0.0.1
endif
ifeq ($(PORT),)
PORT := 8000
endif
start-production:
	gunicorn main:app --workers $(WORKER) --worker-class uvicorn.workers.UvicornWorker --bind $(HOST):$(PORT)

start-worker:
	python ./app/scripts/celeryworker_pre_start.py && celery worker -A app.worker -l info -Q main-queue -c 1

dev:
	make start-worker && make start-app

