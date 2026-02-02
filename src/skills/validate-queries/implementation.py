"""Deterministic implementation for validate-queries skill."""

from typing import Dict, Any, List

from src.utils import Config, SQLValidator


def deterministic_execute(input_data: Dict[str, Any] | None, config: Config, logger) -> Dict[str, Any]:
    """Validate translated queries using deterministic SQL validation."""
    if not input_data:
        raise ValueError("Missing input_data for validation")

    translations_payload = input_data.get("translations", input_data)
    if isinstance(translations_payload, dict) and "data" in translations_payload:
        translations_payload = translations_payload.get("data")

    if not isinstance(translations_payload, dict):
        raise ValueError("Invalid translations input for validation")

    sql_validator = SQLValidator()
    output: Dict[str, Any] = {}

    for folder_name, entries in translations_payload.items():
        if not isinstance(entries, list):
            continue

        folder_results = []
        for entry in entries:
            file_name = entry.get("file_name", "unknown.sql")
            translated_query = entry.get("translated_query")
            translation_status = entry.get("translation_status")

            if translation_status != "SUCCESS" or not translated_query:
                folder_results.append(
                    {
                        "file_name": file_name,
                        "validation_status": "INVALID",
                        "syntax_errors": ["Translation failed or missing translated_query"],
                        "compatibility_issues": [],
                        "warnings": [],
                        "recommendations": ["Re-run translation with agent fallback"],
                        "can_execute": False,
                    }
                )
                continue

            translated_valid, translated_error = sql_validator.validate_syntax(translated_query)
            syntax_errors: List[str] = []
            if not translated_valid:
                syntax_errors.append(str(translated_error))

            incompatibilities = sql_validator.detect_redshift_incompatibilities(translated_query)
            warnings = []
            recommendations = []
            if incompatibilities:
                warnings = [f"Potential incompatibility: {issue}" for issue in incompatibilities]
                recommendations = [
                    "Review Redshift compatibility issues and adjust the query",
                ]

            if syntax_errors:
                validation_status = "INVALID"
                can_execute = False
            elif warnings:
                validation_status = "WARNING"
                can_execute = True
            else:
                validation_status = "VALID"
                can_execute = True

            folder_results.append(
                {
                    "file_name": file_name,
                    "validation_status": validation_status,
                    "syntax_errors": syntax_errors,
                    "compatibility_issues": incompatibilities,
                    "warnings": warnings,
                    "recommendations": recommendations,
                    "can_execute": can_execute,
                }
            )

        output[folder_name] = folder_results

    return output


def validate_output(output: Dict[str, Any]) -> tuple[bool, str]:
    """Validate deterministic validation output.

    If any query is INVALID, trigger agent fallback for a more nuanced assessment.
    """
    if not isinstance(output, dict):
        return False, "Output must be a dictionary"

    for folder_name, entries in output.items():
        if not isinstance(entries, list):
            return False, f"Folder '{folder_name}' must map to a list"
        for entry in entries:
            status = entry.get("validation_status")
            if status == "INVALID":
                return False, f"Invalid validation result in '{folder_name}'"
            if "can_execute" not in entry:
                return False, f"Missing can_execute in '{folder_name}' entry"

    return True, "OK"
