"""Step: Generate reports and summaries"""

import logging
import time
from typing import Dict, List

from src.core import (
    ValidationResult,
    StepResult,
    AgentixLogger,
)
from src.utils import Config


class ReportStep:
    """
    Step 4: Generate comprehensive reports and logs.
    """

    def __init__(self, config: Config, logger: AgentixLogger):
        self.config = config
        self.logger = logger
        self.step_logger = logging.getLogger(__name__)

    def execute(
        self, validation_by_folder: Dict[str, List[ValidationResult]]
    ) -> StepResult:
        """
        Generate reports from validation results.
        """
        start_time = time.time()
        self.step_logger.info("Starting ReportStep")

        # Aggregate statistics
        total_queries = 0
        total_translated = 0
        total_validated = 0
        total_passed = 0

        folder_summaries = {}

        for folder_name, validations in validation_by_folder.items():
            folder_stats = {
                "folder_name": folder_name,
                "total_queries": len(validations),
                "translated": sum(
                    1 for v in validations if v.translation_result.status.value == "SUCCESS"
                ),
                "validated": sum(
                    1 for v in validations if v.status.value in ["PASSED", "FAILED"]
                ),
                "passed": sum(1 for v in validations if v.passed),
                "queries": [],
            }

            for val_result in validations:
                query_detail = {
                    "file": val_result.translation_result.query_metadata.file_name,
                    "table": val_result.translation_result.query_metadata.table_name,
                    "translation_status": val_result.translation_result.status.value,
                    "validation_status": val_result.status.value,
                    "passed": val_result.passed,
                }
                folder_stats["queries"].append(query_detail)

            folder_summaries[folder_name] = folder_stats
            total_queries += folder_stats["total_queries"]
            total_translated += folder_stats["translated"]
            total_validated += folder_stats["validated"]
            total_passed += folder_stats["passed"]

        # Write logs
        self.logger.write_table_logs()
        self.logger.write_folder_logs(folder_summaries)
        summary_file = self.logger.write_summary()

        self.step_logger.info(f"Reports written to {summary_file}")
        self.step_logger.info(f"Summary: {total_passed}/{total_queries} queries passed validation")

        result = StepResult(
            step_name="report",
            status="SUCCESS",
            total_items=total_queries,
            successful_items=total_passed,
            failed_items=total_queries - total_passed,
            details={
                "summary_file": summary_file,
                "folders": list(folder_summaries.keys()),
                "total_translated": total_translated,
                "total_validated": total_validated,
                "pass_rate": (total_passed / total_queries * 100) if total_queries > 0 else 0,
            },
            execution_time_ms=(time.time() - start_time) * 1000,
        )

        self.logger.log_step(result)
        return result
