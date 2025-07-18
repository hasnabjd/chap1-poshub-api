import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app

# Ajouter le répertoire parent au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def client():
    """Fixture pour créer un client de test FastAPI"""
    return TestClient(app)


@pytest.fixture  # preparation de données pour excécuter les tests
def sample_order_data():
    """Fixture avec des données de commande de test"""
    return {"nom_client": "Test Client", "montant": 99.99, "devise": "EUR"}
