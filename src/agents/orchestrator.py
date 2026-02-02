"""Agent orchestrator for managing the translation pipeline"""

import json
import logging
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path

from src.core import AgentixLogger, Config
from src.agents.skill_manager import SkillManager


class PipelineStep:
    """Declarative definition of a pipeline step."""
    
    def __init__(
        self,
        name: str,
        input_builder: Callable[[Dict[str, Any], Config], Dict[str, Any]],
    ):
        self.name = name
        self.input_builder = input_builder


class TranslationOrchestrator:
    """
    Orchestrates the entire translation pipeline using Skills.
    Skills are agent-driven components that read SKILL.md files.
    """

    # Declarative pipeline definition - easy to extend
    PIPELINE_STEPS = [
        PipelineStep(
            name="read-queries",
            input_builder=lambda prev, cfg: {
                "input_path": str(cfg.DATA_INPUT_PATH),
            },
        ),
        PipelineStep(
            name="translate-teradata-to-redshift",
            input_builder=lambda prev, cfg: {
                "queries": prev.get("read-queries"),
            },
        ),
        PipelineStep(
            name="validate-queries",
            input_builder=lambda prev, cfg: {
                "translations": prev.get("translate-teradata-to-redshift"),
            },
        ),
        PipelineStep(
            name="generate-report",
            input_builder=lambda prev, cfg: {
                "read_results": prev.get("read-queries"),
                "translate_results": prev.get("translate-teradata-to-redshift"),
                "validate_results": prev.get("validate-queries"),
                "output_path": str(cfg.DATA_OUTPUT_PATH),
            },
        ),
    ]

    def __init__(self, config: Config):
        self.config = config
        self.logger = AgentixLogger(config.LOGS_PATH, config.LOG_LEVEL)
        self.step_logger = logging.getLogger(__name__)
        self.skill_manager = SkillManager(config)

    def execute_full_pipeline(self, max_retries: Optional[int] = None) -> dict:
        """
        Execute the complete pipeline end-to-end using declarative skill definitions.
        
        This iterates through PIPELINE_STEPS and executes each skill in order,
        passing outputs from one step as inputs to the next.
        """
        if max_retries is None:
            max_retries = self.config.MAX_RETRIES

        self.step_logger.info("=" * 50)
        self.step_logger.info("Starting Translation Pipeline (Agent-Based Skills)")
        self.step_logger.info(f"Config: {self.config.TRANSLATION_STRATEGY} strategy, "
                             f"{max_retries} max retries")
        self.step_logger.info("=" * 50)

        try:
            results = {}
            
            for idx, step in enumerate(self.PIPELINE_STEPS, 1):
                self.step_logger.info(f"\n[{idx}/{len(self.PIPELINE_STEPS)}] Executing {step.name} skill...")
                
                # Build input using the step's input_builder
                input_data = step.input_builder(results, self.config)
                
                # Execute the skill
                result = self.skill_manager.execute_skill(
                    step.name,
                    input_data=input_data,
                )
                
                # Check for errors
                if result.get("status") == "ERROR":
                    self.step_logger.error(f"{step.name} skill failed: {result.get('error')}")
                    return {
                        "status": "error",
                        "error": result.get("error"),
                        "skill": step.name,
                    }
                
                # Store result for next steps
                results[step.name] = result

            self.step_logger.info("\n" + "=" * 50)
            self.step_logger.info("Pipeline Completed Successfully")
            self.step_logger.info("=" * 50)

            # Return all results
            return {
                "status": "success",
                **results,
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
            result = self.skill_manager.execute_skill(
                skill_name,
                input_data=input_data,
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
