"""File handling for queries and results"""

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
from .models import QueryMetadata, QueryType
import logging


class FileHandler:
    """Deterministic file operations for reading and writing queries"""

    def __init__(self, input_path: str, output_path: str):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.logger = logging.getLogger(__name__)

    def read_queries_from_folders(self) -> Dict[str, List[QueryMetadata]]:
        """
        Read all .sql files from input directories.
        Returns dict: {folder_name: [QueryMetadata, ...]}
        
        Deterministic behavior:
        - Reads all .sql files recursively
        - Extracts folder structure
        - Parses metadata from file content
        """
        queries_by_folder = {}

        if not self.input_path.exists():
            self.logger.warning(f"Input path does not exist: {self.input_path}")
            return queries_by_folder

        # Walk through all directories
        for folder_path in sorted(self.input_path.rglob(".")):
            if folder_path.is_dir() and folder_path != self.input_path:
                folder_name = folder_path.relative_to(self.input_path).name
                queries = self._read_folder_queries(folder_path, folder_name)
                if queries:
                    queries_by_folder[folder_name] = queries

        # Also read queries from root input path
        root_queries = self._read_folder_queries(self.input_path, "root")
        if root_queries:
            queries_by_folder["root"] = root_queries

        return queries_by_folder

    def _read_folder_queries(
        self, folder_path: Path, folder_name: str
    ) -> List[QueryMetadata]:
        """Read all SQL files from a specific folder"""
        queries = []

        # Get all .sql files in this folder (not recursive)
        sql_files = sorted(folder_path.glob("*.sql"))

        for sql_file in sql_files:
            try:
                with open(sql_file, "r", encoding="utf-8") as f:
                    query_content = f.read().strip()

                if not query_content:
                    self.logger.warning(f"Empty query file: {sql_file}")
                    continue

                metadata = self._parse_query_metadata(
                    query_content, sql_file, folder_name
                )
                queries.append(metadata)
            except Exception as e:
                self.logger.error(f"Error reading query file {sql_file}: {str(e)}")

        return queries

    def _parse_query_metadata(
        self, query_content: str, file_path: Path, folder_name: str
    ) -> QueryMetadata:
        """Extract metadata from query content"""
        # Detect query type
        query_upper = query_content.upper().strip()
        query_type = QueryType.OTHER

        if query_upper.startswith("SELECT"):
            query_type = QueryType.SELECT
        elif query_upper.startswith("INSERT"):
            query_type = QueryType.INSERT
        elif query_upper.startswith("UPDATE"):
            query_type = QueryType.UPDATE
        elif query_upper.startswith("DELETE"):
            query_type = QueryType.DELETE
        elif query_upper.startswith("MERGE"):
            query_type = QueryType.MERGE

        # Extract table name from query (simple heuristic)
        table_name = self._extract_table_name(query_content, query_type)

        # Detect Teradata-specific functions
        teradata_functions = self._detect_teradata_functions(query_content)

        # Calculate complexity score
        complexity_score = self._calculate_complexity(query_content)

        return QueryMetadata(
            file_name=file_path.name,
            file_path=str(file_path),
            folder_name=folder_name,
            table_name=table_name,
            query_type=query_type,
            original_query=query_content,
            complexity_score=complexity_score,
            has_teradata_functions=len(teradata_functions) > 0,
            teradata_functions=teradata_functions,
        )

    def _extract_table_name(self, query: str, query_type: QueryType) -> str:
        """Extract table name from query - simple extraction"""
        query_upper = query.upper()

        if query_type == QueryType.SELECT:
            if "FROM" in query_upper:
                from_pos = query_upper.find("FROM")
                after_from = query[from_pos + 4:].strip()
                table_name = after_from.split()[0].strip("(").strip()
                return table_name

        elif query_type in [QueryType.INSERT, QueryType.UPDATE, QueryType.DELETE]:
            # These usually have table right after the keyword
            tokens = query_upper.split()
            if query_type == QueryType.INSERT and "INTO" in tokens:
                idx = tokens.index("INTO")
                if idx + 1 < len(tokens):
                    return tokens[idx + 1]
            elif query_type in [QueryType.UPDATE, QueryType.DELETE]:
                if len(tokens) > 1:
                    return tokens[1]

        return "unknown"

    def _detect_teradata_functions(self, query: str) -> List[str]:
        """Detect Teradata-specific functions"""
        teradata_funcs = [
            "SUBSTRING",
            "TRIM",
            "CAST",
            "SEL",
            "QUALIFY",
            "TERA_DATE",
            "PERIOD",
            "RECURSIVE",
        ]

        detected = []
        query_upper = query.upper()

        for func in teradata_funcs:
            if func in query_upper:
                detected.append(func)

        return detected

    def _calculate_complexity(self, query: str) -> float:
        """Calculate query complexity score (0.0 to 1.0)"""
        score = 0.1  # base score

        # Count keywords that indicate complexity
        keywords = [
            ("JOIN", 0.2),
            ("SUBQUERY", 0.15),
            ("UNION", 0.15),
            ("GROUP BY", 0.1),
            ("HAVING", 0.1),
            ("WINDOW", 0.2),
            ("WITH", 0.15),
        ]

        query_upper = query.upper()

        for keyword, weight in keywords:
            if keyword in query_upper:
                score += weight

        # Clamp to 1.0
        return min(score, 1.0)

    def write_translated_query(
        self, folder_name: str, original_filename: str, translated_query: str
    ) -> str:
        """
        Write translated query to output folder structure.
        
        Returns:
            Path to written file
        """
        output_folder = self.output_path / folder_name
        output_folder.mkdir(parents=True, exist_ok=True)

        # Replace .sql with .translated.sql
        output_filename = original_filename.replace(".sql", ".translated.sql")
        output_file = output_folder / output_filename

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(translated_query)

        self.logger.info(f"Wrote translated query to {output_file}")
        return str(output_file)

    def write_json_output(
        self, folder_name: str, filename: str, data: Dict
    ) -> str:
        """Write JSON output to file"""
        output_folder = self.output_path / folder_name
        output_folder.mkdir(parents=True, exist_ok=True)

        output_file = output_folder / filename

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

        self.logger.info(f"Wrote JSON output to {output_file}")
        return str(output_file)

    def ensure_output_path(self) -> None:
        """Ensure output path exists"""
        self.output_path.mkdir(parents=True, exist_ok=True)
