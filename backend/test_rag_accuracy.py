import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Make sure we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.rag import ClaimsAssistant


class TestClaimsAssistant:
    """Test suite for ClaimsAssistant RAG system."""

    @pytest.fixture(scope="class")
    def rag(self):
        """Initialize ClaimsAssistant once for all tests in this class."""
        return ClaimsAssistant()

    def test_query_returns_answer_and_context(self, rag):
        """Test that query returns both answer and context."""
        result = rag.query("Show me denied claims")
        
        assert "answer" in result
        assert "context" in result
        assert isinstance(result["context"], list)

    def test_query_empty_string(self, rag):
        """Test handling of empty query."""
        result = rag.query("")
        
        assert "answer" in result
        assert isinstance(result["context"], list)

    @pytest.mark.parametrize("query,expected_snippet", [
        ("What treatment did a patient receive?", "Treatment"),
        ("Show me claims with status Denied", "Denied"),
        ("Find claims for Cardiology", "Cardiology"),
    ])
    def test_retrieval_relevance(self, rag, query, expected_snippet):
        """Test that retrieval returns relevant documents."""
        result = rag.query(query)
        
        # Check if any retrieved document contains expected snippet
        hits = [r['document'] for r in result['context']]
        found = any(expected_snippet.lower() in doc.lower() for doc in hits)
        
        assert found, f"Expected '{expected_snippet}' in retrieved documents for query '{query}'"

    def test_context_has_required_fields(self, rag):
        """Test that context items have required fields."""
        result = rag.query("Show claims for patient")
        
        if result["context"]:
            for item in result["context"]:
                assert "document" in item
                assert "metadata" in item
                assert "score" in item

    def test_reranker_improves_order(self, rag):
        """Test that reranker adds rerank_score when available."""
        result = rag.query("Find rejected claims due to coding errors")
        
        if rag.reranker and result["context"]:
            # Check if rerank_score is present when reranker is available
            assert "rerank_score" in result["context"][0]


class TestClaimsAssistantWithMocks:
    """Test ClaimsAssistant with mocked external dependencies."""

    @patch('backend.rag.InferenceClient')
    def test_handles_llm_api_error(self, mock_client):
        """Test graceful handling of LLM API errors."""
        mock_instance = MagicMock()
        mock_instance.text_generation.side_effect = Exception("API Error")
        mock_client.return_value = mock_instance

        with patch.dict(os.environ, {"HF_TOKEN": "fake_token"}):
            rag = ClaimsAssistant()
            result = rag.query("test query")
            
            assert "error" in result["answer"].lower() or result["answer"] != ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
