"""Step: Read queries from input folders"""

import logging
import time
from typing import Dict, List
from pathlib import Path

from src.core import QueryMetadata, FileHandler, StepResult, AgentixLogger
from src.utils import Config


class ReadQueriesStep:
    """
    Step 1: Read all SQL queries from input folders.
    Deterministic: Always reads same files, same order.
    """

    def __init__(self, config: Config, logger: AgentixLogger):
        self.config = config
        self.logger = logger
        self.file_handler = FileHandler(config.DATA_INPUT_PATH, config.DATA_OUTPUT_PATH)
        self.step_logger = logging.getLogger(__name__)

    def execute(self) -> tuple[Dict[str, List[QueryMetadata]], StepResult]:
        """
        Execute step and return queries grouped by folder.
        
        Returns:
            (queries_by_folder, step_result)
        """
        start_time = time.time()
        self.step_logger.info("Starting ReadQueriesStep")

        try:
            queries_by_folder = self.file_handler.read_queries_from_folders()

            total_queries = sum(len(q) for q in queries_by_folder.values())
            self.step_logger.info(f"Found {total_queries} queries in {len(queries_by_folder)} folders")

            # Create step result
            result = StepResult(
                step_name="read_queries",
                status="SUCCESS",
                total_items=total_queries,
                successful_items=total_queries,
                failed_items=0,
                details={
                    "folders": list(queries_by_folder.keys()),
                    "total_queries": total_queries,
                    "input_path": self.config.DATA_INPUT_PATH,
                },
                execution_time_ms=(time.time() - start_time) * 1000,
            )

            self.logger.log_step(result)
            return queries_by_folder, result

        except Exception as e:
            self.step_logger.error(f"Error reading queries: {str(e)}", exc_info=True)
            result = StepResult(
                step_name="read_queries",
                status="FAILED",
                total_items=0,
                successful_items=0,
                failed_items=0,
                details={"error": str(e)},
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            self.logger.log_step(result)
            raise
