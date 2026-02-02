"""Deterministic implementation for generate-report skill."""

from typing import Dict, Any, List

from src.utils import Config


def deterministic_execute(input_data: Dict[str, Any] | None, config: Config, logger) -> Dict[str, Any]:
    """Generate a report based on validation results and translation metadata."""
    if not input_data:
        raise ValueError("Missing input_data for report generation")

    validation_payload = input_data.get("validate_results") or input_data.get("validation_results")
    if validation_payload is None:
        validation_payload = input_data

    if isinstance(validation_payload, dict) and "data" in validation_payload:
        validation_payload = validation_payload.get("data")

    if not isinstance(validation_payload, dict):
        raise ValueError("Invalid validation results input for report generation")

    translate_payload = input_data.get("translate_results") or {}
    if isinstance(translate_payload, dict) and "data" in translate_payload:
        translate_payload = translate_payload.get("data")

    read_payload = input_data.get("read_results") or {}
    if isinstance(read_payload, dict) and "data" in read_payload:
        read_payload = read_payload.get("data")

    summary = _build_summary(validation_payload)
    by_folder = _build_folder_summary(validation_payload, translate_payload)
    statistics = _build_statistics(read_payload, translate_payload)

    report = {
        "summary": summary,
        "by_folder": by_folder,
        "statistics": statistics,
        "recommendations": _derive_recommendations(validation_payload),
        "blockers": _derive_blockers(validation_payload),
    }

    return report


def validate_output(output: Dict[str, Any]) -> tuple[bool, str]:
    """Validate deterministic report output."""
    if not isinstance(output, dict):
        return False, "Report output must be a dictionary"
    if "summary" not in output:
        return False, "Report missing 'summary' section"
    required = {"total_queries", "successful", "failed", "warnings", "success_rate", "processed_folders"}
    missing = required - set(output.get("summary", {}).keys())
    if missing:
        return False, f"Report summary missing keys: {missing}"
    return True, "OK"


def _build_summary(validation_payload: Dict[str, Any]) -> Dict[str, Any]:
    total = 0
    successful = 0
    failed = 0
    warnings = 0

    for entries in validation_payload.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            total += 1
            status = entry.get("validation_status")
            if status == "INVALID":
                failed += 1
            elif status == "WARNING":
                warnings += 1
                successful += 1
            else:
                successful += 1

    success_rate = (successful / total * 100) if total > 0 else 0

    return {
        "total_queries": total,
        "successful": successful,
        "failed": failed,
        "warnings": warnings,
        "success_rate": success_rate,
        "processed_folders": len(validation_payload.keys()),
    }


def _build_folder_summary(
    validation_payload: Dict[str, Any],
    translate_payload: Dict[str, Any],
) -> Dict[str, Any]:
    by_folder: Dict[str, Any] = {}

    translation_lookup = _build_translation_lookup(translate_payload)

    for folder_name, entries in validation_payload.items():
        if not isinstance(entries, list):
            continue

        folder_total = len(entries)
        folder_successful = 0
        folder_failed = 0
        folder_warnings = 0
        folder_queries: List[Dict[str, Any]] = []

        for entry in entries:
            status = entry.get("validation_status")
            if status == "INVALID":
                folder_failed += 1
            elif status == "WARNING":
                folder_warnings += 1
                folder_successful += 1
            else:
                folder_successful += 1

            file_name = entry.get("file_name", "unknown.sql")
            translation_status = translation_lookup.get(folder_name, {}).get(file_name, "UNKNOWN")
            issues_count = len(entry.get("syntax_errors", [])) + len(entry.get("compatibility_issues", []))

            folder_queries.append(
                {
                    "file_name": file_name,
                    "status": status or "UNKNOWN",
                    "issues_count": issues_count,
                    "translation_status": translation_status,
                }
            )

        by_folder[folder_name] = {
            "total": folder_total,
            "successful": folder_successful,
            "failed": folder_failed,
            "warnings": folder_warnings,
            "queries": folder_queries,
        }

    return by_folder


def _build_statistics(
    read_payload: Dict[str, Any],
    translate_payload: Dict[str, Any],
) -> Dict[str, Any]:
    by_type: Dict[str, int] = {}
    complexity_distribution = {"simple": 0, "medium": 0, "complex": 0}

    for folder_entries in read_payload.values():
        if not isinstance(folder_entries, list):
            continue
        for entry in folder_entries:
            query_type = entry.get("query_type", "OTHER")
            by_type[query_type] = by_type.get(query_type, 0) + 1

            complexity = entry.get("complexity_score", 0.0)
            if complexity < 0.3:
                complexity_distribution["simple"] += 1
            elif complexity < 0.7:
                complexity_distribution["medium"] += 1
            else:
                complexity_distribution["complex"] += 1

    if not by_type and translate_payload:
        for folder_entries in translate_payload.values():
            if not isinstance(folder_entries, list):
                continue
            by_type["UNKNOWN"] = by_type.get("UNKNOWN", 0) + len(folder_entries)

    return {
        "by_type": by_type,
        "complexity_distribution": complexity_distribution,
    }


def _derive_recommendations(validation_payload: Dict[str, Any]) -> List[str]:
    recommendations: List[str] = []
    for entries in validation_payload.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            recommendations.extend(entry.get("recommendations", []))
    return list(dict.fromkeys(recommendations))


def _derive_blockers(validation_payload: Dict[str, Any]) -> List[str]:
    blockers: List[str] = []
    for entries in validation_payload.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if entry.get("validation_status") == "INVALID":
                blockers.extend(entry.get("syntax_errors", []))
                blockers.extend(entry.get("compatibility_issues", []))
    return list(dict.fromkeys(blockers))


def _build_translation_lookup(translate_payload: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    lookup: Dict[str, Dict[str, str]] = {}
    if not isinstance(translate_payload, dict):
        return lookup

    for folder_name, entries in translate_payload.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            file_name = entry.get("file_name", "unknown.sql")
            translation_status = entry.get("translation_status", "UNKNOWN")
            lookup.setdefault(folder_name, {})[file_name] = translation_status

    return lookup
