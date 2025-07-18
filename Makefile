# Makefile pour PosHub API

.PHONY: help dev test install precommit

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