import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response

from src.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


class TestExternalAPI:
    """Tests for external API integration endpoints"""

    @respx.mock
    def test_external_demo_client_error(self, client):
        """Test external API client error (4xx)"""
        # Mock 404 response
        respx.get("https://httpbin.org/get").mock(
            return_value=Response(404, json={"error": "Not found"})
        )

        # Make the request
        response = client.get("/v1/external-demo")

        # Should handle client errors appropriately
        assert response.status_code in [400, 404, 500]
