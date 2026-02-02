"""Skill Manager - reads SKILL.md files and executes them through Claude"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from anthropic import Anthropic
from src.utils import Config


class SkillManager:
    """Manages skill execution by reading SKILL.md files and passing them to Claude."""

    def __init__(self, config: Config):
        self.config = config
        self.skills_path = Path(__file__).parent.parent / "skills"
        self.client = Anthropic()
        self.logger = logging.getLogger(__name__)
        self.conversation_history = []

    def _load_skill(self, skill_name: str) -> Dict[str, Any]:
        """Load a skill from its SKILL.md file."""
        skill_dir = self.skills_path / skill_name
        skill_file = skill_dir / "SKILL.md"

        if not skill_file.exists():
            raise FileNotFoundError(f"Skill file not found: {skill_file}")

        with open(skill_file, "r") as f:
            content = f.read()

        # Parse YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) < 3:
                raise ValueError(f"Invalid SKILL.md format in {skill_file}")

            frontmatter_str = parts[1]
            instructions = parts[2].strip()

            try:
                frontmatter = yaml.safe_load(frontmatter_str)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML frontmatter in {skill_file}: {e}")

            return {
                "name": frontmatter.get("name", skill_name),
                "description": frontmatter.get("description", ""),
                "instructions": instructions,
                "full_path": str(skill_file),
            }
        else:
            raise ValueError(f"SKILL.md must start with YAML frontmatter: {skill_file}")

    def execute_skill(
        self,
        skill_name: str,
        input_data: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a skill by sending its instructions to Claude.

        Args:
            skill_name: Name of the skill folder (e.g., "read-queries")
            input_data: Context data to provide to Claude (paths, previous results, etc.)
            context: Additional context about the task

        Returns:
            Parsed JSON response from Claude
        """
        # Load the skill
        skill = self._load_skill(skill_name)
        self.logger.info(f"Executing skill: {skill['name']}")

        # Build the prompt
        user_message = self._build_user_prompt(skill, input_data, context)

        # Call Claude
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system="""You are an expert SQL and data migration specialist. 
When executing skills, follow the instructions precisely and return valid JSON responses.
If you encounter an issue, explain it in the JSON response under an "error" field.""",
                messages=[{"role": "user", "content": user_message}],
            )

            response_text = response.content[0].text

            # Try to parse JSON from response
            try:
                # Look for JSON in the response
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    result = {"response": response_text}
            except json.JSONDecodeError:
                self.logger.warning(
                    f"Could not parse JSON from skill response, returning raw response"
                )
                result = {"response": response_text}

            self.logger.info(
                f"Skill '{skill['name']}' completed with status: {result.get('status', 'unknown')}"
            )
            return result

        except Exception as e:
            self.logger.error(f"Error executing skill '{skill_name}': {str(e)}")
            return {
                "status": "ERROR",
                "error": str(e),
                "skill": skill_name,
            }

    def _build_user_prompt(
        self, skill: Dict[str, Any], input_data: Optional[Dict[str, Any]], context: Optional[str]
    ) -> str:
        """Build the user message for Claude."""
        prompt_parts = [
            f"# Executing Skill: {skill['name']}",
            f"\n{skill['description']}",
            f"\n## Instructions\n{skill['instructions']}",
        ]

        if context:
            prompt_parts.append(f"\n## Context\n{context}")

        if input_data:
            prompt_parts.append(f"\n## Input Data\n```json\n{json.dumps(input_data, indent=2)}\n```")

        prompt_parts.append(
            "\n## Execution\nPlease execute this skill and return results in the specified JSON format."
        )

        return "\n".join(prompt_parts)

    def list_skills(self) -> list[str]:
        """List all available skills."""
        if not self.skills_path.exists():
            return []

        skills = []
        for item in self.skills_path.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                skills.append(item.name)

        return sorted(skills)
