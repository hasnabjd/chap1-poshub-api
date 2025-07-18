# Makefile pour PosHub API

.PHONY: help dev test install

help:
	@echo "Commandes disponibles:"
	@echo "  make dev     - Démarre l'API en mode développement"
	@echo "  make test    - Lance les tests"
	@echo "  make install - Installe les dépendances"

# Démarre l'API FastAPI
run-uvicorn:
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Lance les tests
test:
	poetry run pytest

# Installe les dépendances
install:
	poetry install 