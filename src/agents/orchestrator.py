"""Agent orchestrator for managing the translation pipeline"""

import logging
from typing import Optional, List

from src.core import AgentixLogger
from src.utils import Config
from src.steps import ReadQueriesStep, TranslateStep, ValidateStep, ReportStep


class TranslationOrchestrator:
    """
    Orchestrates the entire translation pipeline.
    Manages step execution and retry logic.
    """

    def __init__(self, config: Config):
        self.config = config
        self.logger = AgentixLogger(config.LOGS_PATH, config.LOG_LEVEL)
        self.step_logger = logging.getLogger(__name__)

    def execute_full_pipeline(self, max_retries: Optional[int] = None) -> dict:
        """
        Execute the complete pipeline end-to-end.
        
        Steps:
        1. Read queries
        2. Translate (with retries)
        3. Validate
        4. Generate reports
        """
        if max_retries is None:
            max_retries = self.config.MAX_RETRIES

        self.step_logger.info("=" * 50)
        self.step_logger.info("Starting Translation Pipeline")
        self.step_logger.info(f"Config: {self.config.TRANSLATION_STRATEGY} strategy, "
                             f"{max_retries} max retries")
        self.step_logger.info("=" * 50)

        try:
            # Step 1: Read
            read_step = ReadQueriesStep(self.config, self.logger)
            queries_by_folder, _ = read_step.execute()

            if not queries_by_folder:
                self.step_logger.warning("No queries found to process")
                return {"status": "empty", "message": "No queries found"}

            # Step 2: Translate
            translate_step = TranslateStep(self.config, self.logger)
            translation_results, _ = translate_step.execute(queries_by_folder, max_retries)

            # Step 3: Validate
            validate_step = ValidateStep(self.config, self.logger)
            validation_results, _ = validate_step.execute(translation_results)

            # Step 4: Report
            report_step = ReportStep(self.config, self.logger)
            report_result = report_step.execute(validation_results)

            self.step_logger.info("=" * 50)
            self.step_logger.info("Pipeline Completed Successfully")
            self.step_logger.info(f"Pass Rate: {report_result.success_rate:.1f}%")
            self.step_logger.info("=" * 50)

            return {
                "status": "success",
                "summary": report_result.to_dict(),
                "logs_path": str(self.config.LOGS_PATH),
            }

        except Exception as e:
            self.step_logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "logs_path": str(self.config.LOGS_PATH),
            }

    def execute_step(self, step_name: str, **kwargs) -> dict:
        """
        Execute a single step with provided inputs.
        """
        self.step_logger.info(f"Executing step: {step_name}")

        try:
            if step_name == "read_queries":
                step = ReadQueriesStep(self.config, self.logger)
                result, step_result = step.execute()
                return {
                    "status": "success",
                    "data": result,
                    "step_result": step_result.to_dict(),
                }

            elif step_name == "translate":
                # Requires queries_by_folder input
                queries = kwargs.get("queries_by_folder")
                if not queries:
                    return {"status": "error", "error": "Missing queries_by_folder input"}

                step = TranslateStep(self.config, self.logger)
                max_retries = kwargs.get("max_retries", self.config.MAX_RETRIES)
                result, step_result = step.execute(queries, max_retries)
                return {
                    "status": "success",
                    "data": result,
                    "step_result": step_result.to_dict(),
                }

            elif step_name == "validate":
                # Requires translation_results input
                results = kwargs.get("translation_results")
                if not results:
                    return {"status": "error", "error": "Missing translation_results input"}

                step = ValidateStep(self.config, self.logger)
                result, step_result = step.execute(results)
                return {
                    "status": "success",
                    "data": result,
                    "step_result": step_result.to_dict(),
                }

            elif step_name == "report":
                # Requires validation_results input
                results = kwargs.get("validation_results")
                if not results:
                    return {"status": "error", "error": "Missing validation_results input"}

                step = ReportStep(self.config, self.logger)
                result = step.execute(results)
                return {
                    "status": "success",
                    "step_result": result.to_dict(),
                }

            else:
                return {"status": "error", "error": f"Unknown step: {step_name}"}

        except Exception as e:
            self.step_logger.error(f"Step '{step_name}' failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "step": step_name,
            }

    def list_steps(self) -> List[str]:
        """List available steps"""
        return ["read_queries", "translate", "validate", "report"]
