"""SQL validation and parsing utilities"""

import sqlparse
from typing import List, Dict, Tuple
import logging


class SQLValidator:
    """Validate and parse SQL queries"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_syntax(self, query: str) -> Tuple[bool, str]:
        """
        Basic SQL syntax validation.
        Returns (is_valid, error_message)
        """
        try:
            # Try to parse the SQL
            parsed = sqlparse.parse(query)
            if not parsed:
                return False, "Query could not be parsed"
            return True, ""
        except Exception as e:
            return False, str(e)

    def extract_tables(self, query: str) -> List[str]:
        """Extract table names from query"""
        try:
            parsed = sqlparse.parse(query)[0]
            tables = []

            # Simple extraction logic
            from_seen = False
            for token in parsed.tokens:
                if from_seen and token.ttype is None:
                    table_name = str(token).strip()
                    if table_name and not table_name.upper() in [
                        "WHERE",
                        "GROUP",
                        "ORDER",
                        "LIMIT",
                    ]:
                        tables.append(table_name)
                        from_seen = False

                if token.ttype is sqlparse.tokens.Keyword and str(token).upper() == "FROM":
                    from_seen = True

            return tables
        except Exception as e:
            self.logger.error(f"Error extracting tables: {str(e)}")
            return []

    def extract_columns(self, query: str) -> List[str]:
        """Extract column references from SELECT clause"""
        try:
            parsed = sqlparse.parse(query)[0]
            columns = []
            in_select = False

            for token in parsed.tokens:
                if token.ttype is sqlparse.tokens.Keyword and str(token).upper() == "SELECT":
                    in_select = True
                elif token.ttype is sqlparse.tokens.Keyword and str(token).upper() in [
                    "FROM",
                    "WHERE",
                ]:
                    in_select = False

                if in_select and token.ttype is None:
                    col_str = str(token).strip()
                    if col_str and col_str != "*":
                        # Split by comma
                        parts = col_str.split(",")
                        columns.extend([p.strip() for p in parts if p.strip()])

            return columns
        except Exception as e:
            self.logger.error(f"Error extracting columns: {str(e)}")
            return []

    def detect_redshift_incompatibilities(self, query: str) -> List[str]:
        """Detect Teradata functions incompatible with Redshift"""
        incompatibilities = []
        query_upper = query.upper()

        # Check for known incompatible patterns
        patterns = {
            "QUALIFY": "QUALIFY clause not supported in Redshift",
            "RECURSIVE": "Recursive CTEs may have limited support",
            "PERIOD": "PERIOD syntax not standard in Redshift",
            "SEL": "SEL statement is Teradata-specific",
            "TERA_DATE": "TERA_DATE is Teradata-specific",
        }

        for pattern, message in patterns.items():
            if pattern in query_upper:
                incompatibilities.append(message)

        return incompatibilities
