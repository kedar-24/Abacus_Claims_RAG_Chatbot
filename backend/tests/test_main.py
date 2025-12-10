import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Create a test client with proper lifespan handling."""
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_returns_ok(self, client):
        """Test health endpoint returns OK status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "rag_ready" in data


class TestQueryEndpoint:
    """Tests for the query endpoint."""

    def test_query_valid_request(self, client):
        """Test valid query returns answer and context."""
        response = client.post("/query", json={"query": "diabetes"})
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "context" in data
        assert isinstance(data["context"], list)

    def test_query_missing_payload(self, client):
        """Test missing query field returns validation error."""
        response = client.post("/query", json={})
        assert response.status_code == 422

    def test_query_empty_string(self, client):
        """Test empty query string returns 400 error."""
        response = client.post("/query", json={"query": ""})
        assert response.status_code == 400

    def test_query_whitespace_only(self, client):
        """Test whitespace-only query returns 400 error."""
        response = client.post("/query", json={"query": "   "})
        assert response.status_code == 400


class TestQueryResults:
    """Integration tests for query result quality."""

    def test_query_returns_relevant_context(self, client):
        """Test that queries return relevant documents in context."""
        response = client.post("/query", json={"query": "denied claims"})
        assert response.status_code == 200
        data = response.json()
        
        # Should have at least some context
        assert len(data["context"]) > 0

    def test_context_items_have_required_fields(self, client):
        """Test context items have document, metadata, score fields."""
        response = client.post("/query", json={"query": "test"})
        assert response.status_code == 200
        data = response.json()
        
        if data["context"]:
            for item in data["context"]:
                assert "document" in item
                assert "metadata" in item
                assert "score" in item
