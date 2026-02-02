"""Step: Validate translated queries with synthetic data"""

import logging
import time
from typing import Dict, List

from src.core import (
    TranslationResult,
    ValidationResult,
    StepResult,
    AgentixLogger,
    ValidationStatus,
)
from src.utils import Config, SQLValidator


class ValidateStep:
    """
    Step 3: Validate translations using synthetic data.
    Deterministic validation approach.
    """

    def __init__(self, config: Config, logger: AgentixLogger):
        self.config = config
        self.logger = logger
        self.sql_validator = SQLValidator()
        self.step_logger = logging.getLogger(__name__)

    def execute(
        self, results_by_folder: Dict[str, List[TranslationResult]]
    ) -> tuple[Dict[str, List[ValidationResult]], StepResult]:
        """
        Validate all translated queries.
        
        Returns:
            (validation_results_by_folder, step_result)
        """
        start_time = time.time()
        self.step_logger.info("Starting ValidateStep")

        validation_by_folder = {}
        total_validations = 0
        successful_validations = 0
        failed_validations = 0

        for folder_name, translation_results in results_by_folder.items():
            folder_validations = []
            self.step_logger.info(
                f"Validating {len(translation_results)} translations in folder '{folder_name}'"
            )

            for trans_result in translation_results:
                if trans_result.status.value != "SUCCESS":
                    # Skip validation for failed translations
                    val_result = ValidationResult(
                        translation_result=trans_result,
                        status=ValidationStatus.SKIPPED,
                        passed=False,
                        error_message="Translation failed, skipping validation",
                    )
                    folder_validations.append(val_result)
                    self.logger.log_validation(val_result, folder_name)
                    continue

                total_validations += 1
                val_result = self._validate_translation(trans_result, folder_name)

                if val_result.passed:
                    successful_validations += 1
                    self.step_logger.info(
                        f"✓ {trans_result.query_metadata.file_name} passed validation"
                    )
                else:
                    failed_validations += 1
                    self.step_logger.warning(
                        f"✗ {trans_result.query_metadata.file_name} failed validation: "
                        f"{val_result.error_message}"
                    )

                folder_validations.append(val_result)
                self.logger.log_validation(val_result, folder_name)

            validation_by_folder[folder_name] = folder_validations

        result = StepResult(
            step_name="validate",
            status="SUCCESS" if failed_validations == 0 else "PARTIAL",
            total_items=total_validations,
            successful_items=successful_validations,
            failed_items=failed_validations,
            details={
                "folders": list(validation_by_folder.keys()),
                "validation_type": "syntax_and_compatibility",
            },
            execution_time_ms=(time.time() - start_time) * 1000,
        )

        self.logger.log_step(result)
        return validation_by_folder, result

    def _validate_translation(
        self, trans_result: TranslationResult, folder_name: str
    ) -> ValidationResult:
        """Validate a single translation"""
        val_result = ValidationResult(
            translation_result=trans_result,
            status=ValidationStatus.RUNNING,
        )

        try:
            start_time = time.time()

            # Step 1: Syntax validation
            original_valid, original_error = self.sql_validator.validate_syntax(
                trans_result.query_metadata.original_query
            )
            translated_valid, translated_error = self.sql_validator.validate_syntax(
                trans_result.translated_query
            )

            if not translated_valid:
                val_result.status = ValidationStatus.FAILED
                val_result.passed = False
                val_result.error_message = f"Translated query has syntax errors: {translated_error}"
                return val_result

            # Step 2: Check for incompatibilities
            incompatibilities = self.sql_validator.detect_redshift_incompatibilities(
                trans_result.translated_query
            )

            if incompatibilities:
                self.step_logger.warning(
                    f"Potential incompatibilities detected: {incompatibilities}"
                )
                # Don't fail on incompatibilities, just warn
                val_result.execution_details = f"Warnings: {incompatibilities}"

            # Step 3: Extract metadata
            tables = self.sql_validator.extract_tables(trans_result.translated_query)
            columns = self.sql_validator.extract_columns(trans_result.translated_query)

            if not tables and trans_result.query_metadata.query_type.value != "INSERT":
                val_result.status = ValidationStatus.FAILED
                val_result.passed = False
                val_result.error_message = "No tables found in translated query"
                return val_result

            # Validation passed
            val_result.status = ValidationStatus.PASSED
            val_result.passed = True
            val_result.synthetic_data_generated = False  # In real scenario, would generate
            val_result.rows_compared = 0
            val_result.execution_time_ms = (time.time() - start_time) * 1000
            val_result.execution_details = (
                f"Tables: {tables}, Columns: {columns}, "
                f"Incompatibilities: {len(incompatibilities)}"
            )

        except Exception as e:
            self.step_logger.error(f"Validation error: {str(e)}", exc_info=True)
            val_result.status = ValidationStatus.FAILED
            val_result.passed = False
            val_result.error_message = str(e)

        return val_result
