# Makefile pour PosHub API

.PHONY: help dev test install precommit lint format check-all clean docker-build docker-run docker-test black isort flake8 check-format coverage coverage-check coverage-ci mypy check

# Démarre l'API FastAPI
run-uvicorn:
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Lance les tests
test:
	poetry run pytest

# Check test coverage
coverage:
	poetry run pytest --cov=src

# Run tests with coverage and fail if < 80%
coverage-check:
	poetry run pytest --cov=src --cov-fail-under=80

# Run tests with coverage and fail if < 80% (CI version)
coverage-ci:
	poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Run mypy for static type checking
mypy:
	poetry run mypy src/

# Installe les dépendances
install:
	poetry install 

# Lance pre-commit sur tous les fichiers
precommit:
	poetry run pre-commit run --all-files

# Lint avec flake8
lint:
	poetry run flake8 src/ tests/

# Format avec black
black:
	poetry run black src/ tests/

# Format avec isort
isort:
	poetry run isort src/ tests/

# Format avec black et isort
format: black isort

# Vérifie le formatage sans modifier
check-format:
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/

# Run all checks (mypy + precommit)
check: mypy precommit

# Pipeline complète pour CI
check-all: install lint check-format coverage-ci

# Nettoie les caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	poetry run pre-commit clean

# Docker commands
docker-build:
	docker build -t poshub-api .

docker-run:
	docker run -p 8000:8000 poshub-api

docker-test:
	docker run -d -p 8000:8000 --name poshub-test poshub-api
	sleep 10
	curl -f http://127.0.0.1:8000/health || exit 1
	docker stop poshub-test
	docker rm poshub-test