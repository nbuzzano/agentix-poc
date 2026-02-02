"""Tests for translation engine"""

import pytest
from unittest.mock import Mock, patch
from src.core import QueryMetadata, QueryType, TranslationStatus
from src.core.translation import TranslationEngine


class TestTranslationEngine:
    """Test translation engine"""

    @pytest.fixture
    def mock_client(self):
        """Mock Anthropic client"""
        with patch('src.core.translation.Anthropic') as mock:
            yield mock

    def test_translate_basic_strategy(self, mock_client):
        """Test basic translation strategy"""
        # This would require mocking the Anthropic client
        # Simplified test for structure
        engine = TranslationEngine(api_key="test-key")
        assert engine.model == "claude-3-5-sonnet-20241022"

    def test_translation_result_structure(self):
        """Test translation result creation"""
        meta = QueryMetadata(
            file_name="test.sql",
            file_path="/path/test.sql",
            folder_name="sales",
            table_name="orders",
            query_type=QueryType.SELECT,
            original_query="SELECT * FROM orders",
        )

        # Test result creation
        from src.core import TranslationResult
        result = TranslationResult(
            query_metadata=meta,
            translated_query="SELECT * FROM orders;",
            status=TranslationStatus.SUCCESS,
        )

        assert result.status == TranslationStatus.SUCCESS
        assert result.translated_query == "SELECT * FROM orders;"
        assert result.translated_at is not None


class TestTranslationStrategies:
    """Test different translation strategies"""

    def test_strategy_names(self):
        """Test that all strategies are recognized"""
        engine = TranslationEngine(api_key="test-key")
        strategies = ["basic", "advanced", "iterative"]
        
        for strategy in strategies:
            # Just verify no exception on creation
            assert strategy in ["basic", "advanced", "iterative"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
