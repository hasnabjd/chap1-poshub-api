import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Client de test FastAPI"""
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """Token d'authentification pour les tests"""
    response = client.post("/auth/token/orders-write?user_id=test-user")
    assert response.status_code == 200
    return response.json()["access_token"]


def test_generate_token_success(client):
    """Test de génération d'un token JWT"""
    response = client.post("/auth/token/orders-write?user_id=test-user")

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600
    assert "orders:write" in data["scopes"]
    assert "orders:read" in data["scopes"]


def test_generate_custom_token(client):
    """Test de génération d'un token personnalisé"""
    token_request = {
        "user_id": "custom-user",
        "scopes": ["orders:write", "products:read"],
        "expires_in_minutes": 60,
    }

    response = client.post("/auth/token", json=token_request)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["expires_in"] == 3600  # 60 minutes en secondes
    assert data["scopes"] == ["orders:write", "products:read"]


def test_protected_route_without_token(client):
    """Test d'accès à une route protégée sans token"""
    order_data = {"customer_id": "123", "items": [{"product_id": "456", "quantity": 2}]}

    response = client.post("/orders", json=order_data)

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_protected_route_with_invalid_token(client):
    """Test d'accès à une route protégée avec token invalide"""
    invalid_token = "invalid.token.here"

    order_data = {"customer_id": "123", "items": [{"product_id": "456", "quantity": 2}]}

    response = client.post(
        "/orders", headers={"Authorization": f"Bearer {invalid_token}"}, json=order_data
    )

    assert response.status_code == 401
    assert "Token invalide" in response.json()["detail"]


def test_protected_route_with_valid_token(client, auth_token):
    """Test d'accès à une route protégée avec token valide"""
    order_data = {"customer_id": "123", "items": [{"product_id": "456", "quantity": 2}]}

    response = client.post(
        "/orders", headers={"Authorization": f"Bearer {auth_token}"}, json=order_data
    )

    # Le test devrait réussir l'authentification (peut échouer sur la logique métier)
    # mais ne devrait pas échouer sur l'authentification (401/403)
    assert response.status_code != 401
    assert response.status_code != 403


def test_token_without_required_scope(client):
    """Test avec un token qui n'a pas les scopes requis"""
    # Créer un token sans le scope orders:write
    token_request = {
        "user_id": "limited-user",
        "scopes": ["orders:read"],  # Pas de orders:write
        "expires_in_minutes": 30,
    }

    token_response = client.post("/auth/token", json=token_request)
    limited_token = token_response.json()["access_token"]

    order_data = {"customer_id": "123", "items": [{"product_id": "456", "quantity": 2}]}

    response = client.post(
        "/orders", headers={"Authorization": f"Bearer {limited_token}"}, json=order_data
    )

    assert response.status_code == 403
    assert "Scopes insuffisants" in response.json()["detail"]


def test_bearer_token_format(client):
    """Test avec un format de token Bearer incorrect"""
    token_response = client.post("/auth/token/orders-write")
    token = token_response.json()["access_token"]

    # Test sans "Bearer " prefix
    response = client.post(
        "/orders",
        headers={"Authorization": token},  # Manque "Bearer "
        json={"customer_id": "123", "items": []},
    )

    assert response.status_code == 401
