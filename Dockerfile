# Dockerfile pour PosHub API
FROM python:3.13-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installer Poetry
RUN pip install poetry==2.1.3

# Configurer Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copier le fichier de configuration Poetry
COPY pyproject.toml ./

# Générer le lock file et installer les dépendances
RUN poetry lock && poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Copier le code source
COPY src/ ./src/

# Exposer le port
EXPOSE 8000

# Commande par défaut
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 