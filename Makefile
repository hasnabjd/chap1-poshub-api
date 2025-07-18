# Makefile pour PosHub API

.PHONY: help dev test install precommit lint format check-all clean docker-build docker-run docker-test

# Démarre l'API FastAPI
run-uvicorn:
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Lance les tests
test:
	poetry run pytest

# Installe les dépendances
install:
	poetry install 

# Lance pre-commit sur tous les fichiers
precommit:
	poetry run pre-commit run --all-files

# Lint avec flake8
lint:
	poetry run flake8 src/ tests/

# Format avec black et isort
format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

# Vérifie le formatage sans modifier
check-format:
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/

# Type checking avec mypy
type-check:
	poetry run mypy src/

# Pipeline complète pour CI
check-all: install lint check-format type-check test

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