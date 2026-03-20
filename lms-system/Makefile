.PHONY: help install dev test run clean docker-build docker-up docker-down docker-logs migrate createsuperuser collectstatic

# Variables
PYTHON := python
PIP := pip
MANAGE := cd backend && $(PYTHON) manage.py
DOCKER_COMPOSE := docker-compose -f docker/docker-compose.yml

# Default target
.DEFAULT_GOAL := help

## help: Show this help message
help:
	@echo "LMS System - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

## install: Install Python dependencies
install:
	$(PIP) install -r backend/requirements.txt

## install-dev: Install development dependencies
install-dev:
	$(PIP) install -r backend/requirements/development.txt

## dev: Run development server
dev:
	$(MANAGE) runserver 0.0.0.0:8000

## test: Run tests
test:
	$(MANAGE) test

## test-cov: Run tests with coverage
test-cov:
	cd backend && coverage run --source='.' manage.py test && coverage report

## migrate: Run database migrations
migrate:
	$(MANAGE) migrate

## makemigrations: Create new migrations
makemigrations:
	$(MANAGE) makemigrations

## createsuperuser: Create superuser
createsuperuser:
	$(MANAGE) createsuperuser

## collectstatic: Collect static files
collectstatic:
	$(MANAGE) collectstatic --noinput

## clean: Remove compiled Python files and cache
clean:
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
	find . -name '*.pyo' -delete 2>/dev/null || true
	find . -name '.pytest_cache' -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name '.coverage' -delete 2>/dev/null || true
	find . -name 'htmlcov' -type d -exec rm -rf {} + 2>/dev/null || true

## lint: Run code linters
lint:
	cd backend && flake8 .

## format: Format code with black
format:
	cd backend && black .

## docker-build: Build Docker images
docker-build:
	$(DOCKER_COMPOSE) build

## docker-up: Start Docker containers
docker-up:
	$(DOCKER_COMPOSE) up -d

## docker-down: Stop Docker containers
docker-down:
	$(DOCKER_COMPOSE) down

## docker-logs: Show Docker logs
docker-logs:
	$(DOCKER_COMPOSE) logs -f

## docker-ps: Show running containers
docker-ps:
	$(DOCKER_COMPOSE) ps

## docker-restart: Restart Docker containers
docker-restart:
	$(DOCKER_COMPOSE) restart

## docker-migrate: Run migrations in Docker
docker-migrate:
	$(DOCKER_COMPOSE) exec backend python manage.py migrate

## docker-shell: Open Django shell in Docker
docker-shell:
	$(DOCKER_COMPOSE) exec backend python manage.py shell

## docker-db-shell: Open database shell in Docker
docker-db-shell:
	$(DOCKER_COMPOSE) exec db psql -U lms_user -d lms_db

## reset-db: Reset database (WARNING: destroys all data)
reset-db:
	$(MANAGE) reset_db --noinput

## load-fixtures: Load initial data
load-fixtures:
	$(MANAGE) loaddata backend/fixtures/initial_data.json

## dump-data: Dump database to fixtures
dump-data:
	$(MANAGE) dumpdata --indent 2 > backend/fixtures/dump_$(shell date +%Y%m%d_%H%M%S).json