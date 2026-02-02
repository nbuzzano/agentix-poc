"""Base Skill class for step execution with deterministic-first and agent fallback."""

from __future__ import annotations

import logging
from typing import Any, Tuple

from src.core import AgentixLogger, StepResult
from src.utils import Config


class SkillNotApplicable(Exception):
    """Raised when deterministic execution does not apply and should fallback to agent."""


class SkillExecutionError(Exception):
    """Raised when a skill fails after all retries."""


class SkillBase:
    """
    Base class for Skills (agentic steps).
    First attempt is deterministic when applicable, fallback to agent on retry.
    """

    skill_name: str = "skill"

    def __init__(self, config: Config, logger: AgentixLogger):
        self.config = config
        self.logger = logger
        self.step_logger = logging.getLogger(self.__class__.__name__)

    def execute(self, *args: Any, max_retries: int | None = None, **kwargs: Any) -> Tuple[Any, StepResult]:
        """Execute the skill with deterministic-first and agent fallback on retry."""
        retries = max_retries if max_retries is not None else self.config.MAX_RETRIES

        last_error: str | None = None

        try:
            return self.deterministic_execute(*args, **kwargs)
        except SkillNotApplicable as e:
            last_error = str(e)
            self.step_logger.info(
                f"Deterministic execution not applicable for '{self.skill_name}': {last_error}"
            )
        except Exception as e:
            last_error = str(e)
            self.step_logger.warning(
                f"Deterministic execution failed for '{self.skill_name}': {last_error}"
            )

        # Retry with agent fallback
        for attempt in range(2, retries + 1):
            try:
                return self.agent_execute(*args, attempt_number=attempt, last_error=last_error, **kwargs)
            except Exception as e:
                last_error = str(e)
                self.step_logger.warning(
                    f"Agent fallback failed for '{self.skill_name}' on attempt {attempt}: {last_error}"
                )

        raise SkillExecutionError(
            f"Skill '{self.skill_name}' failed after {retries} attempts. Last error: {last_error}"
        )

    def deterministic_execute(self, *args: Any, **kwargs: Any) -> Tuple[Any, StepResult]:
        """Deterministic (Python-based) execution. Override in subclasses."""
        raise NotImplementedError

    def agent_execute(
        self,
        *args: Any,
        attempt_number: int,
        last_error: str | None,
        **kwargs: Any,
    ) -> Tuple[Any, StepResult]:
        """Agent-based fallback execution. Override in subclasses."""
        raise NotImplementedError