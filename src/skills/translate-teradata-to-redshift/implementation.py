"""Deterministic implementation for translate-teradata-to-redshift skill."""

from typing import Dict, Any

from src.core import FileHandler, Config, SQLValidator


def deterministic_execute(input_data: Dict[str, Any] | None, config: Config, logger) -> Dict[str, Any]:
    """Translate queries deterministically when no incompatibilities are found."""
    if not input_data:
        raise ValueError("Missing input_data for translation")

    queries_payload = input_data.get("queries", input_data)
    if isinstance(queries_payload, dict) and "data" in queries_payload:
        queries_payload = queries_payload.get("data")

    if not isinstance(queries_payload, dict):
        raise ValueError("Invalid queries input for translation")

    sql_validator = SQLValidator()
    file_handler = FileHandler(config.DATA_INPUT_PATH, config.DATA_OUTPUT_PATH)

    output: Dict[str, Any] = {}
    for folder_name, entries in queries_payload.items():
        if not isinstance(entries, list):
            continue

        folder_results = []
        for entry in entries:
            original_query = entry.get("original_query")
            file_name = entry.get("file_name", "unknown.sql")

            if not original_query:
                folder_results.append(
                    {
                        "file_name": file_name,
                        "original_query": original_query or "",
                        "translated_query": None,
                        "translation_status": "FAILED",
                        "issues": ["Missing original_query"],
                        "notes": "Deterministic translation skipped due to missing query",
                    }
                )
                continue

            incompatibilities = sql_validator.detect_redshift_incompatibilities(original_query)
            if incompatibilities:
                folder_results.append(
                    {
                        "file_name": file_name,
                        "original_query": original_query,
                        "translated_query": None,
                        "translation_status": "PARTIAL",
                        "issues": incompatibilities,
                        "notes": "Incompatibilities detected; requires agent translation",
                    }
                )
                continue

            # No incompatibilities, deterministic pass-through
            translated_query = original_query
            file_handler.write_translated_query(folder_name, file_name, translated_query)

            folder_results.append(
                {
                    "file_name": file_name,
                    "original_query": original_query,
                    "translated_query": translated_query,
                    "translation_status": "SUCCESS",
                    "issues": [],
                    "notes": "No changes required; query compatible with Redshift",
                }
            )

        output[folder_name] = folder_results

    return output


def validate_output(output: Dict[str, Any]) -> tuple[bool, str]:
    """Validation for deterministic translation output.

    If any query is not SUCCESS, we trigger agent fallback.
    """
    if not isinstance(output, dict):
        return False, "Output must be a dictionary"

    for folder_name, entries in output.items():
        if not isinstance(entries, list):
            return False, f"Folder '{folder_name}' must map to a list"
        for entry in entries:
            status = entry.get("translation_status")
            if status != "SUCCESS":
                return False, f"Non-success translation in '{folder_name}': {status}"
            if not entry.get("translated_query"):
                return False, f"Missing translated_query in '{folder_name}' entry"

    return True, "OK"
