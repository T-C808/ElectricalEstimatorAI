PYTHON ?= python3.12
API_DIR := apps/api
WEB_DIR := apps/web

.PHONY: dev api-install web-install install migrate seed test lint format

dev:
	docker compose up --build

api-install:
	cd $(API_DIR) && $(PYTHON) -m venv .venv
	cd $(API_DIR) && .venv/bin/python -m pip install --upgrade pip
	cd $(API_DIR) && .venv/bin/python -m pip install -e ".[dev]"

web-install:
	cd $(WEB_DIR) && npm install

install: api-install web-install

migrate:
	docker compose run --rm api alembic upgrade head

seed:
	docker compose run --rm api python -m app.services.seed

test:
	cd $(API_DIR) && .venv/bin/python -m pytest
	cd $(WEB_DIR) && npm test -- --run

lint:
	cd $(API_DIR) && .venv/bin/ruff check app tests
	cd $(WEB_DIR) && npm run lint

format:
	cd $(API_DIR) && .venv/bin/ruff format app tests
	cd $(WEB_DIR) && npm run format
