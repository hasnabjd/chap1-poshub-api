# PosHub API

API pour PosHub construite avec FastAPI.

## Démarrage

```bash
# Démarrer le serveur en mode développement avec rechargement automatique
poetry run uvicorn src.main:app --reload
```

Le serveur démarre avec :
- Un client HTTP unique créé dans le lifespan de l'application
- Stocké dans `app.state.http`
- Géré automatiquement (création/fermeture)

## Endpoints

### Orders

#### POST /orders

Crée une nouvelle commande.

**Request Body:**
```json
{
    "nom_client": "hasna",
    "montant": 99.99,
    "devise": "EUR"
}
```

**Response (201 Created):**
```json
{
    "order": "550e8400-e29b-41d4-a716-446655440000",
    "nom_client": "hasna",
    "montant": 99.99,
    "devise": "EUR",
    "created_by": null
}
```

#### GET /orders/{order_id}

Récupère une commande par son ID.

**Parameters:**
- `order_id`: UUID de la commande (généré lors de la création)

**Response (200 OK):**
```json
{
    "order": "550e8400-e29b-41d4-a716-446655440000",
    "nom_client": "hasna",
    "montant": 99.99,
    "devise": "EUR",
    "created_by": null
}
```

**Erreurs:**
- 404 Not Found: Commande non trouvée

### External API Demo

#### GET /external-demo

Endpoint de démonstration qui appelle httpbin.org en utilisant le client HTTP partagé.

**Response (200 OK):**
```json
{
    "args": {
        "demo": "test"
    },
    "headers": {
        // headers de la requête
    },
    "origin": "your.ip.address",
    "url": "https://httpbin.org/get?demo=test"
}
```

**Erreurs:**
- 502 Bad Gateway: Erreur serveur ou réseau
- 504 Gateway Timeout: Timeout (>10s)


## Client (navigateur/curl) → Uvicorn → FastAPI → httpx.AsyncClient → Services Externes

## Communication du Client HTTP Unique dans FastAPI : 
lifespan (création) 
  → get_http_client (récupération) 
    → route (injection) 
      → safe_get (utilisation)


## Workflow d'un système de "catch global" 
safe_get → raise TimeoutError → route (pas de catch) → FastAPI → handler