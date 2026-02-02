"""Step: Translate queries from Teradata to Redshift"""

import logging
import time
from typing import Dict, List

from src.core import (
    QueryMetadata,
    TranslationResult,
    FileHandler,
    StepResult,
    AgentixLogger,
    TranslationEngine,
)
from src.utils import Config


class TranslateStep:
    """
    Step 2: Translate queries using Claude with retry logic.
    """

    def __init__(self, config: Config, logger: AgentixLogger):
        self.config = config
        self.logger = logger
        self.file_handler = FileHandler(config.DATA_INPUT_PATH, config.DATA_OUTPUT_PATH)
        self.translation_engine = TranslationEngine()
        self.step_logger = logging.getLogger(__name__)

    def execute(
        self,
        queries_by_folder: Dict[str, List[QueryMetadata]],
        max_retries: int = 3,
    ) -> tuple[Dict[str, List[TranslationResult]], StepResult]:
        """
        Translate all queries with retry logic.
        
        Returns:
            (results_by_folder, step_result)
        """
        start_time = time.time()
        self.step_logger.info("Starting TranslateStep")

        results_by_folder = {}
        total_queries = 0
        successful = 0
        failed = 0

        for folder_name, queries in queries_by_folder.items():
            folder_results = []
            self.step_logger.info(f"Translating {len(queries)} queries in folder '{folder_name}'")

            for query_meta in queries:
                total_queries += 1
                result = self._translate_with_retries(
                    query_meta, folder_name, max_retries
                )

                if result.status.value == "SUCCESS":
                    successful += 1
                    # Write translated query
                    self.file_handler.write_translated_query(
                        folder_name,
                        query_meta.file_name,
                        result.translated_query,
                    )
                else:
                    failed += 1

                folder_results.append(result)
                self.logger.log_translation(result, folder_name)

            results_by_folder[folder_name] = folder_results

        result = StepResult(
            step_name="translate",
            status="SUCCESS" if failed == 0 else "PARTIAL",
            total_items=total_queries,
            successful_items=successful,
            failed_items=failed,
            details={
                "folders": list(results_by_folder.keys()),
                "strategy": self.config.TRANSLATION_STRATEGY,
                "max_retries": max_retries,
            },
            execution_time_ms=(time.time() - start_time) * 1000,
        )

        self.logger.log_step(result)
        return results_by_folder, result

    def _translate_with_retries(
        self,
        query_meta: QueryMetadata,
        folder_name: str,
        max_retries: int,
    ) -> TranslationResult:
        """Translate with retry logic using different strategies"""
        strategies = ["basic", "advanced", "iterative"]
        last_result = None

        for attempt in range(1, max_retries + 1):
            strategy = strategies[(attempt - 1) % len(strategies)]
            self.step_logger.debug(
                f"Attempt {attempt}/{max_retries} for {query_meta.file_name} "
                f"using strategy '{strategy}'"
            )

            try:
                result = self.translation_engine.translate(
                    query_meta,
                    strategy=strategy,
                    attempt_number=attempt,
                )
                last_result = result

                if result.status.value == "SUCCESS":
                    # Validate translation
                    is_valid, reason = self.translation_engine.validate_translation(
                        query_meta.original_query,
                        result.translated_query,
                    )
                    if is_valid:
                        self.step_logger.info(
                            f"✓ {query_meta.file_name} translated successfully on attempt {attempt}"
                        )
                        return result
                    else:
                        self.step_logger.warning(f"Translation validation failed: {reason}")
                        # Continue to next attempt

            except Exception as e:
                self.step_logger.warning(
                    f"Translation error on attempt {attempt}: {str(e)}"
                )
                # Continue to next attempt

        # All retries exhausted
        if last_result is None:
            from src.core import TranslationStatus

            last_result = TranslationResult(
                query_metadata=query_meta,
                status=TranslationStatus.FAILED,
                error_message="All translation attempts failed",
            )

        self.step_logger.error(
            f"✗ Failed to translate {query_meta.file_name} after {max_retries} attempts"
        )
        return last_result
