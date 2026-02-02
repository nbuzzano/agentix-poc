"""Agent orchestrator for managing the translation pipeline"""

import json
import logging
from typing import Optional, List
from pathlib import Path

from src.core import AgentixLogger
from src.utils import Config
from src.agents.skill_manager import SkillManager


class TranslationOrchestrator:
    """
    Orchestrates the entire translation pipeline using Skills.
    Skills are agent-driven components that read SKILL.md files.
    """

    def __init__(self, config: Config):
        self.config = config
        self.logger = AgentixLogger(config.LOGS_PATH, config.LOG_LEVEL)
        self.step_logger = logging.getLogger(__name__)
        self.skill_manager = SkillManager(config)

    def execute_full_pipeline(self, max_retries: Optional[int] = None) -> dict:
        """
        Execute the complete pipeline end-to-end using Skills.
        
        Skills executed in order:
        1. read-queries: Catalog SQL files
        2. translate-teradata-to-redshift: Translate to Redshift syntax
        3. validate-queries: Validate translated queries
        4. generate-report: Create comprehensive reports
        """
        if max_retries is None:
            max_retries = self.config.MAX_RETRIES

        self.step_logger.info("=" * 50)
        self.step_logger.info("Starting Translation Pipeline (Agent-Based Skills)")
        self.step_logger.info(f"Config: {self.config.TRANSLATION_STRATEGY} strategy, "
                             f"{max_retries} max retries")
        self.step_logger.info("=" * 50)

        try:
            # Skill 1: Read Queries
            self.step_logger.info("\n[1/4] Executing read-queries skill...")
            read_input = {
                "input_path": str(self.config.DATA_INPUT_PATH),
                "file_extensions": [".sql", ".txt"],
            }
            read_result = self.skill_manager.execute_skill(
                "read-queries",
                input_data=read_input,
                context="Read and catalog all Teradata SQL queries from the input directory.",
            )

            if read_result.get("status") == "ERROR":
                self.step_logger.error(f"read-queries skill failed: {read_result.get('error')}")
                return {
                    "status": "error",
                    "error": read_result.get("error"),
                    "skill": "read-queries",
                }

            # Skill 2: Translate
            self.step_logger.info("\n[2/4] Executing translate-teradata-to-redshift skill...")
            translate_input = {
                "queries": read_result,
                "target_dialect": "redshift",
                "optimization_level": "advanced",
            }
            translate_result = self.skill_manager.execute_skill(
                "translate-teradata-to-redshift",
                input_data=translate_input,
                context="Translate the Teradata queries to Redshift-compatible SQL. "
                       "Handle QUALIFY clauses, TIMESTAMP WITH TIME ZONE, and other dialect differences.",
            )

            if translate_result.get("status") == "ERROR":
                self.step_logger.error(f"translate skill failed: {translate_result.get('error')}")
                return {
                    "status": "error",
                    "error": translate_result.get("error"),
                    "skill": "translate-teradata-to-redshift",
                }

            # Skill 3: Validate
            self.step_logger.info("\n[3/4] Executing validate-queries skill...")
            validate_input = {
                "translations": translate_result,
                "target_database": "redshift",
            }
            validate_result = self.skill_manager.execute_skill(
                "validate-queries",
                input_data=validate_input,
                context="Validate that all translated queries are syntactically correct and compatible with Redshift.",
            )

            if validate_result.get("status") == "ERROR":
                self.step_logger.error(f"validate skill failed: {validate_result.get('error')}")
                return {
                    "status": "error",
                    "error": validate_result.get("error"),
                    "skill": "validate-queries",
                }

            # Skill 4: Generate Report
            self.step_logger.info("\n[4/4] Executing generate-report skill...")
            report_input = {
                "read_results": read_result,
                "translate_results": translate_result,
                "validate_results": validate_result,
                "output_path": str(self.config.DATA_OUTPUT_PATH),
            }
            report_result = self.skill_manager.execute_skill(
                "generate-report",
                input_data=report_input,
                context="Generate comprehensive reports and logs of the migration process.",
            )

            if report_result.get("status") == "ERROR":
                self.step_logger.error(f"report skill failed: {report_result.get('error')}")
                return {
                    "status": "error",
                    "error": report_result.get("error"),
                    "skill": "generate-report",
                }

            self.step_logger.info("\n" + "=" * 50)
            self.step_logger.info("Pipeline Completed Successfully")
            self.step_logger.info("=" * 50)

            return {
                "status": "success",
                "read_results": read_result,
                "translate_results": translate_result,
                "validate_results": validate_result,
                "report": report_result,
                "logs_path": str(self.config.LOGS_PATH),
            }

        except Exception as e:
            self.step_logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "logs_path": str(self.config.LOGS_PATH),
            }

    def execute_skill(self, skill_name: str, input_data: Optional[dict] = None, **kwargs) -> dict:
        """
        Execute a single skill.
        
        Args:
            skill_name: Name of the skill folder (e.g., "read-queries")
            input_data: Input data for the skill
            **kwargs: Additional context or parameters
            
        Returns:
            Result from the skill execution
        """
        self.step_logger.info(f"Executing skill: {skill_name}")

        try:
            context = kwargs.get("context", "")
            result = self.skill_manager.execute_skill(
                skill_name,
                input_data=input_data,
                context=context,
            )
            return {
                "status": "success" if result.get("status") != "ERROR" else "error",
                "data": result,
            }
        except Exception as e:
            self.step_logger.error(f"Skill '{skill_name}' failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "skill": skill_name,
            }

    def list_skills(self) -> List[str]:
        """List available skills"""
        return self.skill_manager.list_skills()
