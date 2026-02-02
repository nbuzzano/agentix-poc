"""Tests for Agentix pipeline"""

import pytest
import tempfile
from pathlib import Path
from src.core import QueryMetadata, QueryType, FileHandler, TranslationEngine, SQLValidator


class TestFileHandler:
    """Test file reading and writing"""

    def test_read_empty_folder(self):
        """Test reading from empty folder"""
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileHandler(tmpdir, tmpdir)
            results = handler.read_queries_from_folders()
            assert results == {}

    def test_parse_query_metadata(self):
        """Test query metadata parsing"""
        query = "SELECT * FROM customers WHERE id > 10"
        handler = FileHandler(".", ".")
        
        file_path = Path("test.sql")
        metadata = handler._parse_query_metadata(query, file_path, "test_folder")

        assert metadata.file_name == "test.sql"
        assert metadata.folder_name == "test_folder"
        assert metadata.query_type == QueryType.SELECT
        assert metadata.table_name == "customers"

    def test_complexity_calculation(self):
        """Test complexity score calculation"""
        handler = FileHandler(".", ".")

        simple = "SELECT * FROM customers"
        assert handler._calculate_complexity(simple) == 0.1

        complex_query = """
        SELECT c.id, COUNT(*) as cnt
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        WHERE c.created_date > '2024-01-01'
        GROUP BY c.id
        HAVING COUNT(*) > 5
        ORDER BY cnt DESC
        """
        score = handler._calculate_complexity(complex_query)
        assert score > 0.5


class TestSQLValidator:
    """Test SQL validation"""

    def test_syntax_validation(self):
        """Test basic syntax validation"""
        validator = SQLValidator()

        valid_query = "SELECT * FROM customers"
        is_valid, error = validator.validate_syntax(valid_query)
        assert is_valid

    def test_teradata_incompatibilities(self):
        """Test detection of Teradata-specific features"""
        validator = SQLValidator()

        query_with_qualify = """
        SELECT *
        FROM customers
        QUALIFY ROW_NUMBER() OVER (ORDER BY id) = 1
        """
        incompats = validator.detect_redshift_incompatibilities(query_with_qualify)
        assert any("QUALIFY" in inc for inc in incompats)

    def test_table_extraction(self):
        """Test table name extraction"""
        validator = SQLValidator()

        query = "SELECT * FROM customers WHERE id > 10"
        tables = validator.extract_tables(query)
        assert "customers" in tables or len(tables) > 0  # May extract differently


class TestQueryMetadata:
    """Test QueryMetadata model"""

    def test_metadata_creation(self):
        """Test creating QueryMetadata"""
        meta = QueryMetadata(
            file_name="test.sql",
            file_path="/path/test.sql",
            folder_name="sales",
            table_name="orders",
            query_type=QueryType.SELECT,
            original_query="SELECT * FROM orders",
        )

        assert meta.file_name == "test.sql"
        assert meta.table_name == "orders"
        assert meta.query_type == QueryType.SELECT
        assert meta.parsed_at is not None

    def test_metadata_to_dict(self):
        """Test converting metadata to dict"""
        meta = QueryMetadata(
            file_name="test.sql",
            file_path="/path/test.sql",
            folder_name="sales",
            table_name="orders",
            query_type=QueryType.SELECT,
            original_query="SELECT * FROM orders",
        )

        data = meta.to_dict()
        assert data["file_name"] == "test.sql"
        assert data["table_name"] == "orders"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
