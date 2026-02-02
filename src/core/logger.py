"""Logging system for Agentix"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from .models import TranslationResult, ValidationResult, StepResult


class AgentixLogger:
    """Centralized logging for all pipeline operations"""

    def __init__(self, logs_path: str = "./logs", log_level: str = "INFO"):
        self.logs_path = Path(logs_path)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger("agentix")
        self.logger.setLevel(getattr(logging, log_level))

        # File handler
        log_file = self.logs_path / "agentix.log"
        fh = logging.FileHandler(log_file)
        fh.setLevel(getattr(logging, log_level))

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, log_level))

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        # Storage for structured data
        self.table_logs: Dict[str, List[Dict]] = {}
        self.folder_logs: Dict[str, Dict] = {}
        self.step_results: List[StepResult] = []

    def log_translation(
        self, result: TranslationResult, folder_name: str
    ) -> None:
        """Log translation result"""
        table_name = result.query_metadata.table_name
        self.logger.info(
            f"Translation [{folder_name}/{table_name}]: "
            f"{result.status.value} (attempt {result.attempt_number})"
        )

        if table_name not in self.table_logs:
            self.table_logs[table_name] = []

        self.table_logs[table_name].append(
            {
                "timestamp": datetime.now().isoformat(),
                "folder": folder_name,
                "type": "translation",
                "result": result.to_dict(),
            }
        )

    def log_validation(
        self, result: ValidationResult, folder_name: str
    ) -> None:
        """Log validation result"""
        table_name = result.translation_result.query_metadata.table_name
        self.logger.info(
            f"Validation [{folder_name}/{table_name}]: "
            f"{result.status.value} - Passed: {result.passed}"
        )

        if table_name not in self.table_logs:
            self.table_logs[table_name] = []

        self.table_logs[table_name].append(
            {
                "timestamp": datetime.now().isoformat(),
                "folder": folder_name,
                "type": "validation",
                "result": result.to_dict(),
            }
        )

    def log_step(self, result: StepResult) -> None:
        """Log step result"""
        self.logger.info(
            f"Step '{result.step_name}': {result.status} "
            f"({result.successful_items}/{result.total_items} successful)"
        )
        self.step_results.append(result)

    def log_error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Log error"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)

    def write_table_logs(self) -> Dict[str, str]:
        """Write individual table logs to files"""
        output_files = {}
        tables_path = self.logs_path / "tables"
        tables_path.mkdir(exist_ok=True)

        for table_name, logs in self.table_logs.items():
            safe_name = table_name.replace("/", "_").replace("\\", "_")
            output_file = tables_path / f"{safe_name}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "table_name": table_name,
                        "total_entries": len(logs),
                        "logs": logs,
                    },
                    f,
                    indent=2,
                    default=str,
                )

            output_files[table_name] = str(output_file)
            self.logger.debug(f"Wrote table logs to {output_file}")

        return output_files

    def write_folder_logs(self, folder_summaries: Dict[str, Dict]) -> Dict[str, str]:
        """Write folder summary logs to files"""
        output_files = {}
        folders_path = self.logs_path / "folders"
        folders_path.mkdir(exist_ok=True)

        for folder_name, summary in folder_summaries.items():
            safe_name = folder_name.replace("/", "_").replace("\\", "_")
            output_file = folders_path / f"{safe_name}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, default=str)

            output_files[folder_name] = str(output_file)
            self.logger.debug(f"Wrote folder logs to {output_file}")

        return output_files

    def write_summary(self) -> str:
        """Write overall summary log"""
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tables": len(self.table_logs),
            "step_results": [step.to_dict() for step in self.step_results],
            "table_count": len(self.table_logs),
            "tables": list(self.table_logs.keys()),
        }

        summary_file = self.logs_path / "summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, default=str)

        self.logger.info(f"Wrote summary to {summary_file}")
        return str(summary_file)

    def get_table_summary(self, table_name: str) -> Dict[str, Any]:
        """Get summary for a specific table"""
        if table_name not in self.table_logs:
            return {}

        logs = self.table_logs[table_name]
        translations = [l for l in logs if l["type"] == "translation"]
        validations = [l for l in logs if l["type"] == "validation"]

        successful_translations = sum(
            1 for t in translations if t["result"]["status"] == "SUCCESS"
        )
        successful_validations = sum(
            1 for v in validations if v["result"]["passed"]
        )

        return {
            "table_name": table_name,
            "total_logs": len(logs),
            "translations_attempted": len(translations),
            "translations_successful": successful_translations,
            "validations_attempted": len(validations),
            "validations_successful": successful_validations,
            "last_update": logs[-1]["timestamp"] if logs else None,
        }
