# Makefile pour PosHub API

.PHONY: help dev test install precommit lint format check-all clean docker-build docker-run docker-test sam-build sam-validate sam-local-invoke sam-deploy sam-test-local sam-test-aws create-layer export-poetry-layer assume-role assume-role-with-export

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

# Pipeline complète pour CI
check-all: install check-format coverage-ci


# SAM commands
sam-build:
	sam build -t sam-min.yml



sam-validate:
	sam validate -t sam-min.yml

sam-local-invoke:
	sam local invoke FastApiFunctionH -t sam-min.yml -e event.json

sam-deploy:
	sam deploy --template-file sam-min.yml --stack-name poshub-app-iac-h --s3-bucket poshub-dev-bucket --capabilities CAPABILITY_IAM

sam-stack-delete:
	sam delete --stack-name poshub-app-iac-h

# Export Poetry layer (corrigé pour Windows)
export-poetry-layer:
	rmdir /s /q layers\python-deps
	mkdir -p layers/python-deps/python
	poetry export -f requirements.txt --output layers/python-deps/requirements.txt --without-hashes
	pip install -r layers/python-deps/requirements.txt -t layers/python-deps/python --platform manylinux2014_x86_64 --only-binary=:all: --no-deps
	cd layers && powershell Compress-Archive -Path layers/python-deps/python -DestinationPath layers/python-deps-layer.zip -Force

# STS commands
assume-role:
	aws sts assume-role \
		--role-arn "arn:aws:iam::471448382724:role/poshub-lambda-role-h" \
		--role-session-name "poshub-session"
