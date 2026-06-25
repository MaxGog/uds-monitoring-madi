run:
	python -m main

sync:
	uv sync

init-migrate:
	alembic init -t async backend/migrations

gen-migrations:
	alembic revision --autogenerate -m "init_models"

up-all:
	alembic upgrade head

up:
	alembic upgrade +1

down-all:
	alembic downgrade base

down:
	alembic downgrade -1
	