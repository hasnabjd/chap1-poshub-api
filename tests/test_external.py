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
    def test_external_demo_success(self, client):
        """Test successful external API call"""
        # Mock the external API response
        respx.get("https://httpbin.org/get").mock(
            return_value=Response(
                200,
                json={
                    "args": {"demo": "SMCP", "timestamp": "auto"},
                    "headers": {
                        "Accept": "application/json",
                        "Host": "httpbin.org",
                        "User-Agent": "python-httpx/0.27.0",
                    },
                    "origin": "203.0.113.1",
                    "url": "https://httpbin.org/get?demo=SMCP&timestamp=auto",
                },
            )
        )

        # Make the request
        response = client.get("/v1/external-demo")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "args" in data
        assert data["args"]["demo"] == "SMCP"
        assert data["args"]["timestamp"] == "auto"
        assert "headers" in data
        assert "origin" in data

    @respx.mock
    def test_external_demo_timeout(self, client):
        """Test external API timeout handling"""
        # Mock timeout by not providing a response
        respx.get("https://httpbin.org/get").mock(
            side_effect=Exception("Request timeout")
        )

        # Make the request
        response = client.get("/v1/external-demo")

        # Should handle the error gracefully
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()

    @respx.mock
    def test_external_demo_network_error(self, client):
        """Test external API network error handling"""
        # Mock network error
        respx.get("https://httpbin.org/get").mock(
            return_value=Response(500, json={"error": "Internal Server Error"})
        )

        # Make the request
        response = client.get("/v1/external-demo")

        # Should handle server errors
        assert response.status_code in [500, 502, 504]

    @respx.mock
    def test_external_demo_invalid_json(self, client):
        """Test external API with invalid JSON response"""
        # Mock invalid JSON response
        respx.get("https://httpbin.org/get").mock(
            return_value=Response(200, text="invalid json content")
        )

        # Make the request
        response = client.get("/v1/external-demo")

        # Should handle JSON parsing errors
        assert response.status_code == 500

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


@pytest.mark.asyncio
class TestExternalAPIAsync:
    """Async tests for external API integration"""

    @respx.mock
    async def test_external_demo_async_success(self):
        """Test async external API call success"""
        # Mock successful response
        respx.get("https://httpbin.org/get").mock(
            return_value=Response(
                200,
                json={
                    "args": {"demo": "SMCP", "timestamp": "auto"},
                    "headers": {"Accept": "application/json"},
                    "origin": "203.0.113.1",
                    "url": "https://httpbin.org/get?demo=SMCP&timestamp=auto",
                },
            )
        )

        # Test with async client
        async with TestClient(app) as client:
            response = await client.get("/v1/external-demo")

            assert response.status_code == 200
            data = response.json()
            assert "args" in data
            assert data["args"]["demo"] == "SMCP"

    @respx.mock
    async def test_external_demo_async_multiple_calls(self):
        """Test multiple concurrent external API calls"""
        # Mock the response for multiple calls
        respx.get("https://httpbin.org/get").mock(
            return_value=Response(
                200,
                json={
                    "args": {"demo": "SMCP", "timestamp": "auto"},
                    "headers": {"Accept": "application/json"},
                    "origin": "203.0.113.1",
                    "url": "https://httpbin.org/get?demo=SMCP&timestamp=auto",
                },
            )
        )

        # Make multiple async calls
        async with TestClient(app) as client:
            # Simulate concurrent requests
            responses = []
            for i in range(3):
                response = await client.get("/v1/external-demo")
                responses.append(response)

            # All should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert "args" in data
                assert data["args"]["demo"] == "SMCP"


class TestExternalAPIIntegration:
    """Integration tests for external API (with real network calls)"""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_external_demo_real_call(self, client):
        """Test real external API call (marked as slow integration test)"""
        # This test makes a real HTTP call to httpbin.org
        # It's marked as slow and integration so it can be skipped in CI
        response = client.get("/v1/external-demo")

        # Should work with real API (if network is available)
        if response.status_code == 200:
            data = response.json()
            assert "args" in data
            assert data["args"]["demo"] == "SMCP"
            assert "url" in data
            assert "httpbin.org" in data["url"]
        else:
            # If network fails, that's also acceptable for this test
            pytest.skip("Real external API not available")

    def test_external_demo_correlation_id(self, client):
        """Test that external calls include correlation ID"""
        # This test verifies the correlation ID middleware works
        response = client.get("/v1/external-demo")

        # Should have correlation ID in response headers
        assert "x-correlation-id" in response.headers

        # Correlation ID should be a UUID-like string
        correlation_id = response.headers["x-correlation-id"]
        assert len(correlation_id) > 0
        assert "-" in correlation_id  # UUID format check
