"""Deterministic implementation for read-queries skill."""

from typing import Dict, Any

from src.core import FileHandler, QueryMetadata, Config


def deterministic_execute(input_data: Dict[str, Any] | None, config: Config, logger) -> Dict[str, Any]:
    """Read and catalog SQL queries from input directory using Python code."""
    input_path = None
    if input_data:
        input_path = input_data.get("input_path")

    file_handler = FileHandler(input_path or config.DATA_INPUT_PATH, config.DATA_OUTPUT_PATH)
    queries_by_folder = file_handler.read_queries_from_folders()

    output: Dict[str, Any] = {}
    for folder_name, queries in queries_by_folder.items():
        output[folder_name] = [_serialize_query_metadata(q) for q in queries]

    return output


def validate_output(output: Dict[str, Any]) -> tuple[bool, str]:
    """Validate deterministic output structure for read-queries skill."""
    if not isinstance(output, dict):
        return False, "Output must be a dictionary"

    for folder_name, entries in output.items():
        if not isinstance(entries, list):
            return False, f"Folder '{folder_name}' must map to a list"
        for entry in entries:
            if not isinstance(entry, dict):
                return False, f"Entry in '{folder_name}' must be a dictionary"
            required_keys = {"file_name", "query_type", "original_query"}
            missing = required_keys - set(entry.keys())
            if missing:
                return False, f"Missing keys {missing} in '{folder_name}' entry"
            if not entry.get("original_query"):
                return False, f"Empty original_query in '{folder_name}' entry"

    return True, "OK"


def _serialize_query_metadata(query: QueryMetadata) -> Dict[str, Any]:
    """Convert QueryMetadata to the skill output schema."""
    table_name = query.table_name if query.table_name and query.table_name != "unknown" else None
    tables = [table_name] if table_name else []

    return {
        "file_name": query.file_name,
        "query_type": query.query_type.value,
        "tables": tables,
        "teradata_functions": list(query.teradata_functions or []),
        "complexity_score": query.complexity_score,
        "query_preview": query.original_query[:200],
        "original_query": query.original_query,
    }
